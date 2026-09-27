"""E7.114 pre-execution validation.

This module performs deterministic, side-effect-free validation of a frozen
ScopeLock. It does not execute proof commands, mutate progress, or authorize
execution. A caller may proceed only from an all-PASS report.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import os
from pathlib import Path
import shutil

from gnosis.self_learning.e7_106_selection import SelectionRecord, selection_digest
from gnosis.self_learning.e7_114_scope_lock import ScopeLock, verify_scope_lock
from gnosis.self_learning.e7_114_runtime_attestation import attest_checkout


class PreflightError(ValueError):
    """Raised when preflight cannot establish a safe execution boundary."""


@dataclass(frozen=True)
class PreflightCheck:
    check_id: str
    status: str
    detail: str


@dataclass(frozen=True)
class PreflightReport:
    scope_lock_id: str
    target_commit_sha: str
    checks: tuple[PreflightCheck, ...]
    integrity_digest: str

    @property
    def status(self) -> str:
        if all(check.status == "PASS" for check in self.checks):
            return "PASS"
        if any(check.status == "FAIL" for check in self.checks):
            return "FAIL"
        return "BLOCKED"


def _digest(scope_lock_id: str, target_sha: str, checks: tuple[PreflightCheck, ...]) -> str:
    payload = {
        "scope_lock_id": scope_lock_id,
        "target_commit_sha": target_sha,
        "checks": [
            {"check_id": c.check_id, "status": c.status, "detail": c.detail}
            for c in checks
        ],
    }
    return sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _check(check_id: str, status: str, detail: str) -> PreflightCheck:
    if status not in {"PASS", "FAIL", "BLOCKED"}:
        raise PreflightError(f"invalid preflight status: {status}")
    return PreflightCheck(check_id, status, detail)


def run_preflight(
    scope_lock: ScopeLock,
    *,
    repository_root: str | os.PathLike[str],
    resolved_commit_sha: str,
    resolved_branch_ref: str | None = None,
    selection_record: SelectionRecord | None = None,
) -> PreflightReport:
    """Validate a frozen scope without executing or mutating anything."""
    checks: list[PreflightCheck] = []
    root = Path(repository_root)

    selection_ok = (
        selection_record is not None
        and selection_record.selection_record_id == scope_lock.selection_record_id
        and selection_record.repository == scope_lock.repository
        and selection_record.target_commit_sha.lower() == scope_lock.target_commit_sha.lower()
        and selection_digest(selection_record) == scope_lock.selection_record_digest
    )
    checks.append(
        _check(
            "selection_binding",
            "PASS" if selection_ok else "FAIL",
            "frozen E7.106 selection matches scope lock"
            if selection_ok
            else "frozen E7.106 selection is missing or does not match scope lock",
        )
    )

    checks.append(
        _check(
            "scope_integrity",
            "PASS" if verify_scope_lock(scope_lock) else "FAIL",
            "scope lock integrity is valid"
            if verify_scope_lock(scope_lock)
            else "scope lock is invalid or tampered",
        )
    )

    if not root.is_dir():
        checks.append(_check("repository_access", "FAIL", "repository root is unavailable"))
    else:
        checks.append(_check("repository_access", "PASS", "repository root is accessible"))

    sha_ok = (
        isinstance(resolved_commit_sha, str)
        and resolved_commit_sha.lower() == scope_lock.target_commit_sha.lower()
    )
    checks.append(
        _check(
            "exact_commit",
            "PASS" if sha_ok else "FAIL",
            "resolved commit matches locked SHA"
            if sha_ok
            else "resolved commit does not match locked SHA",
        )
    )

    attestation = attest_checkout(root, scope_lock.target_commit_sha)
    checks.append(
        _check(
            "runtime_checkout_attestation",
            attestation.status,
            "runtime checkout attestation matches locked SHA"
            if attestation.status == "PASS"
            else f"runtime checkout attestation failed: {attestation.actual_head_sha or 'unavailable'}",
        )
    )

    if resolved_branch_ref is None or resolved_branch_ref == scope_lock.branch_ref:
        checks.append(_check("ref_identity", "PASS", "resolved ref matches locked ref"))
    else:
        checks.append(_check("ref_identity", "FAIL", "resolved ref does not match locked ref"))

    required_paths = scope_lock.implementation_paths + scope_lock.runtime_paths
    missing = [p for p in required_paths if not (root / p).is_file()]
    checks.append(
        _check(
            "required_paths",
            "PASS" if not missing else "FAIL",
            "all locked implementation/runtime paths exist"
            if not missing
            else "missing paths: " + ", ".join(missing),
        )
    )

    missing_commands: list[str] = []
    for command in scope_lock.commands:
        try:
            executable = command.split()[0]
        except IndexError:
            executable = ""
        if not executable or shutil.which(executable) is None:
            missing_commands.append(command)
    checks.append(
        _check(
            "commands",
            "PASS" if not missing_commands else "FAIL",
            "all locked command executables are available"
            if not missing_commands
            else "missing command executables: " + ", ".join(missing_commands),
        )
    )

    missing_env = [
        prerequisite
        for prerequisite in scope_lock.environment_prerequisites
        if shutil.which(prerequisite) is None
    ]
    checks.append(
        _check(
            "environment",
            "PASS" if not missing_env else "FAIL",
            "all environment prerequisites are available"
            if not missing_env
            else "missing environment prerequisites: " + ", ".join(missing_env),
        )
    )

    bad_evidence = []
    for destination in scope_lock.evidence_destinations:
        path = root / destination
        if not path.is_dir() or not os.access(path, os.W_OK):
            bad_evidence.append(destination)
    checks.append(
        _check(
            "evidence_capture",
            "PASS" if not bad_evidence else "FAIL",
            "evidence destinations are writable"
            if not bad_evidence
            else "unavailable/unwritable evidence destinations: " + ", ".join(bad_evidence),
        )
    )

    checks.append(
        _check(
            "policy_revisions",
            "PASS"
            if scope_lock.evidence_policy_revision
            and scope_lock.verification_matrix_revision
            and scope_lock.progress_policy_revision
            else "FAIL",
            "all required policy revisions are bound",
        )
    )

    checks.append(
        _check(
            "stop_conditions",
            "PASS" if scope_lock.stop_conditions else "FAIL",
            "deterministic stop conditions are bound",
        )
    )

    checks_tuple = tuple(checks)
    return PreflightReport(
        scope_lock_id=scope_lock.scope_lock_id,
        target_commit_sha=scope_lock.target_commit_sha,
        checks=checks_tuple,
        integrity_digest=_digest(
            scope_lock.scope_lock_id, scope_lock.target_commit_sha, checks_tuple
        ),
    )


def assert_preflight_ready(report: PreflightReport) -> None:
    """Fail closed unless every preflight check explicitly passed."""
    if report.status != "PASS":
        raise PreflightError("proof execution is not preflight-ready")
