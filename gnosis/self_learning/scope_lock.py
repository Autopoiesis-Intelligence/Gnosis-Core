"""Immutable scope-lock primitives for the first governed proof run.

E7.114 defines a pre-execution record. It fixes the exact target commit,
selected criteria, paths, commands, evidence destinations and stop conditions.
It grants no execution authority.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Iterable


@dataclass(frozen=True)
class ScopeLock:
    batch_id: str
    scope_lock_id: str
    repository: str
    ref: str
    target_commit_sha: str
    selected_contract_ids: tuple[str, ...]
    selected_criterion_ids: tuple[str, ...]
    implementation_paths: tuple[str, ...]
    test_runtime_paths: tuple[str, ...]
    commands: tuple[str, ...]
    expected_outcomes: tuple[str, ...]
    evidence_destinations: tuple[str, ...]
    environment_prerequisites: tuple[str, ...]
    stop_conditions: tuple[str, ...]
    evidence_policy_revision: str
    verification_matrix_revision: str
    progress_calculation_policy_revision: str
    status: str = "LOCKED"
    revision: int = 1
    invalidation_reason: str | None = None

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def create_scope_lock(
    *,
    batch_id: str,
    repository: str,
    ref: str,
    target_commit_sha: str,
    selected_contract_ids: Iterable[str],
    selected_criterion_ids: Iterable[str],
    implementation_paths: Iterable[str],
    test_runtime_paths: Iterable[str],
    commands: Iterable[str],
    expected_outcomes: Iterable[str],
    evidence_destinations: Iterable[str],
    environment_prerequisites: Iterable[str],
    stop_conditions: Iterable[str],
    evidence_policy_revision: str,
    verification_matrix_revision: str,
    progress_calculation_policy_revision: str,
) -> ScopeLock:
    values = {
        "batch_id": batch_id,
        "repository": repository,
        "ref": ref,
        "target_commit_sha": target_commit_sha,
        "selected_contract_ids": tuple(selected_contract_ids),
        "selected_criterion_ids": tuple(selected_criterion_ids),
        "implementation_paths": tuple(implementation_paths),
        "test_runtime_paths": tuple(test_runtime_paths),
        "commands": tuple(commands),
        "expected_outcomes": tuple(expected_outcomes),
        "evidence_destinations": tuple(evidence_destinations),
        "environment_prerequisites": tuple(environment_prerequisites),
        "stop_conditions": tuple(stop_conditions),
        "evidence_policy_revision": evidence_policy_revision,
        "verification_matrix_revision": verification_matrix_revision,
        "progress_calculation_policy_revision": progress_calculation_policy_revision,
    }
    if not batch_id or not repository or not ref or not target_commit_sha:
        raise ValueError("batch, repository, ref and target commit are required")
    for name, value in values.items():
        if isinstance(value, tuple) and not value:
            raise ValueError(f"{name} must not be empty")
    canonical = json.dumps(values, sort_keys=True, separators=(",", ":"))
    scope_lock_id = "sha256:" + hashlib.sha256(canonical.encode()).hexdigest()
    return ScopeLock(scope_lock_id=scope_lock_id, **values)


def validate_scope_lock(
    lock: ScopeLock,
    *,
    actual_commit_sha: str,
    available_paths: Iterable[str],
    progress_before: object,
    progress_after: object,
) -> None:
    if lock.status != "LOCKED":
        raise ValueError("scope lock is not executable")
    if actual_commit_sha != lock.target_commit_sha:
        raise ValueError("scope lock target commit does not match actual commit")
    available = set(available_paths)
    required = set(lock.implementation_paths) | set(lock.test_runtime_paths)
    missing = sorted(required - available)
    if missing:
        raise ValueError("scope lock paths unavailable: " + ", ".join(missing))
    if progress_before != progress_after:
        raise ValueError("scope locking must not change progress")


def invalidate_scope_lock(lock: ScopeLock, *, reason: str) -> ScopeLock:
    if not reason:
        raise ValueError("invalidation reason is required")
    return ScopeLock(
        **{
            **lock.as_dict(),
            "status": "INVALIDATED",
            "invalidation_reason": reason,
        }
    )


def serialize_scope_lock(lock: ScopeLock) -> str:
    return json.dumps(lock.as_dict(), sort_keys=True, separators=(",", ":"))
