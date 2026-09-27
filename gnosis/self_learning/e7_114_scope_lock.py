"""E7.114 concrete scope-lock boundary.

The scope lock freezes the exact execution target before any proof execution.
It has no progress side effects and becomes invalid when any locked execution
identity changes.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from hashlib import sha256
import json


class ScopeLockError(ValueError):
    """Raised when a scope lock cannot be created or validated."""


@dataclass(frozen=True)
class ScopeLock:
    batch_id: str
    scope_lock_id: str
    repository: str
    branch_ref: str
    target_commit_sha: str
    contract_ids: tuple[str, ...]
    criterion_ids: tuple[str, ...]
    implementation_paths: tuple[str, ...]
    runtime_paths: tuple[str, ...]
    expected_outcomes: tuple[str, ...]
    evidence_destinations: tuple[str, ...]
    environment_prerequisites: tuple[str, ...]
    stop_conditions: tuple[str, ...]
    evidence_policy_revision: str
    verification_matrix_revision: str
    progress_policy_revision: str
    integrity_digest: str
    status: str = "VALID"
    revision: int = 1


def _require_nonempty(name: str, value: str) -> None:
    if not value or not value.strip():
        raise ScopeLockError(f"{name} is required")


def _require_sha(value: str) -> None:
    if len(value) != 40 or any(c not in "0123456789abcdef" for c in value.lower()):
        raise ScopeLockError("target_commit_sha must be a 40-character SHA-1")


def _payload(lock: ScopeLock) -> dict:
    return {
        "batch_id": lock.batch_id,
        "scope_lock_id": lock.scope_lock_id,
        "repository": lock.repository,
        "branch_ref": lock.branch_ref,
        "target_commit_sha": lock.target_commit_sha,
        "contract_ids": list(lock.contract_ids),
        "criterion_ids": list(lock.criterion_ids),
        "implementation_paths": list(lock.implementation_paths),
        "runtime_paths": list(lock.runtime_paths),
        "expected_outcomes": list(lock.expected_outcomes),
        "evidence_destinations": list(lock.evidence_destinations),
        "environment_prerequisites": list(lock.environment_prerequisites),
        "stop_conditions": list(lock.stop_conditions),
        "evidence_policy_revision": lock.evidence_policy_revision,
        "verification_matrix_revision": lock.verification_matrix_revision,
        "progress_policy_revision": lock.progress_policy_revision,
        "revision": lock.revision,
    }


def _digest(lock: ScopeLock) -> str:
    raw = json.dumps(_payload(lock), sort_keys=True, separators=(",", ":")).encode()
    return sha256(raw).hexdigest()


def create_scope_lock(
    *,
    batch_id: str,
    scope_lock_id: str,
    repository: str,
    branch_ref: str,
    target_commit_sha: str,
    contract_ids: tuple[str, ...],
    criterion_ids: tuple[str, ...],
    implementation_paths: tuple[str, ...],
    runtime_paths: tuple[str, ...],
    expected_outcomes: tuple[str, ...],
    evidence_destinations: tuple[str, ...],
    environment_prerequisites: tuple[str, ...],
    stop_conditions: tuple[str, ...],
    evidence_policy_revision: str,
    verification_matrix_revision: str,
    progress_policy_revision: str,
) -> ScopeLock:
    for name, value in (
        ("batch_id", batch_id),
        ("scope_lock_id", scope_lock_id),
        ("repository", repository),
        ("branch_ref", branch_ref),
        ("evidence_policy_revision", evidence_policy_revision),
        ("verification_matrix_revision", verification_matrix_revision),
        ("progress_policy_revision", progress_policy_revision),
    ):
        _require_nonempty(name, value)

    _require_sha(target_commit_sha)
    if not contract_ids or not criterion_ids:
        raise ScopeLockError("frozen contract and criterion selections are required")
    if not implementation_paths or not runtime_paths:
        raise ScopeLockError("implementation and runtime paths are required")
    if not expected_outcomes or not evidence_destinations:
        raise ScopeLockError("expected outcomes and evidence destinations are required")
    if not environment_prerequisites or not stop_conditions:
        raise ScopeLockError("environment prerequisites and stop conditions are required")

    lock = ScopeLock(
        batch_id=batch_id,
        scope_lock_id=scope_lock_id,
        repository=repository,
        branch_ref=branch_ref,
        target_commit_sha=target_commit_sha.lower(),
        contract_ids=tuple(contract_ids),
        criterion_ids=tuple(criterion_ids),
        implementation_paths=tuple(implementation_paths),
        runtime_paths=tuple(runtime_paths),
        expected_outcomes=tuple(expected_outcomes),
        evidence_destinations=tuple(evidence_destinations),
        environment_prerequisites=tuple(environment_prerequisites),
        stop_conditions=tuple(stop_conditions),
        evidence_policy_revision=evidence_policy_revision,
        verification_matrix_revision=verification_matrix_revision,
        progress_policy_revision=progress_policy_revision,
        integrity_digest="",
    )
    return replace(lock, integrity_digest=_digest(lock))


def verify_scope_lock(lock: ScopeLock) -> bool:
    if lock.status != "VALID":
        return False
    _require_sha(lock.target_commit_sha)
    return lock.integrity_digest == _digest(lock)


def invalidate_scope_lock(lock: ScopeLock, *, reason: str) -> ScopeLock:
    _require_nonempty("reason", reason)
    if lock.status == "INVALIDATED":
        return lock
    return replace(lock, status="INVALIDATED", revision=lock.revision + 1)


def assert_target_commit(lock: ScopeLock, resolved_sha: str) -> None:
    _require_sha(resolved_sha)
    if not verify_scope_lock(lock):
        raise ScopeLockError("scope lock is invalid or tampered")
    if resolved_sha.lower() != lock.target_commit_sha:
        raise ScopeLockError("target commit does not match locked SHA")


def revise_scope_lock(lock: ScopeLock, **changes) -> ScopeLock:
    if lock.status != "INVALIDATED":
        raise ScopeLockError("scope lock must be invalidated before revision")
    changes.pop("status", None)
    changes["revision"] = lock.revision + 1
    changes["status"] = "VALID"
    candidate = replace(lock, **changes, integrity_digest="")
    return replace(candidate, integrity_digest=_digest(candidate))
