"""E7.114 concrete scope-lock boundary."""
from __future__ import annotations
from dataclasses import dataclass, replace
from hashlib import sha256
import json
import shlex

class ScopeLockError(ValueError):
    """Raised when a scope lock cannot be created or validated."""

@dataclass(frozen=True)
class ScopeLock:
    batch_id: str
    selection_record_id: str
    selection_record_digest: str
    scope_lock_id: str
    repository: str
    branch_ref: str
    target_commit_sha: str
    contract_ids: tuple[str, ...]
    criterion_ids: tuple[str, ...]
    implementation_paths: tuple[str, ...]
    runtime_paths: tuple[str, ...]
    commands: tuple[str, ...]
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
    if not value or not value.strip(): raise ScopeLockError(f"{name} is required")

def _require_sha(value: str) -> None:
    if len(value) != 40 or any(c not in "0123456789abcdef" for c in value.lower()): raise ScopeLockError("target_commit_sha must be a 40-character SHA-1")

def _require_digest(value: str) -> None:
    if len(value) != 64 or any(c not in "0123456789abcdef" for c in value.lower()): raise ScopeLockError("selection_record_digest must be a 64-character SHA-256")

def _payload(lock: ScopeLock) -> dict:
    return {k: list(v) if isinstance(v, tuple) else v for k,v in {
        "batch_id":lock.batch_id,"selection_record_id":lock.selection_record_id,"selection_record_digest":lock.selection_record_digest,
        "scope_lock_id":lock.scope_lock_id,"repository":lock.repository,"branch_ref":lock.branch_ref,
        "target_commit_sha":lock.target_commit_sha,"contract_ids":lock.contract_ids,"criterion_ids":lock.criterion_ids,
        "implementation_paths":lock.implementation_paths,"runtime_paths":lock.runtime_paths,"commands":lock.commands,
        "expected_outcomes":lock.expected_outcomes,"evidence_destinations":lock.evidence_destinations,
        "environment_prerequisites":lock.environment_prerequisites,"stop_conditions":lock.stop_conditions,
        "evidence_policy_revision":lock.evidence_policy_revision,"verification_matrix_revision":lock.verification_matrix_revision,
        "progress_policy_revision":lock.progress_policy_revision,"revision":lock.revision}.items()}


_SHELL_EXECUTABLES = {"sh", "bash", "dash", "zsh", "fish", "csh", "tcsh", "ksh", "cmd", "powershell", "pwsh"}
_SHELL_OPERATORS = {";", "&&", "||", "|", "|&", ">", ">>", "<", "<<", "&"}


def _validate_command(command: str) -> None:
    _require_nonempty("command", command)
    try:
        argv = shlex.split(command, posix=True)
    except ValueError as exc:
        raise ScopeLockError(f"invalid locked command syntax: {exc}") from exc
    if not argv:
        raise ScopeLockError("locked command is empty")
    if any(token in _SHELL_OPERATORS for token in argv):
        raise ScopeLockError("shell operators are forbidden in locked commands")
    executable = argv[0].rsplit("/", 1)[-1].lower()
    if executable in _SHELL_EXECUTABLES:
        raise ScopeLockError("shell executables are forbidden in locked commands")
    if executable in {"python", "python3", "py"} and "-c" in argv:
        raise ScopeLockError("interpreter -c execution is forbidden in locked commands")

def _digest(lock: ScopeLock) -> str:
    return sha256(json.dumps(_payload(lock), sort_keys=True, separators=(",",":")).encode()).hexdigest()

def create_scope_lock(*, batch_id, selection_record_id, selection_record_digest, scope_lock_id, repository, branch_ref, target_commit_sha, contract_ids, criterion_ids, implementation_paths, runtime_paths, commands, expected_outcomes, evidence_destinations, environment_prerequisites, stop_conditions, evidence_policy_revision, verification_matrix_revision, progress_policy_revision):
    for name,value in (("batch_id",batch_id),("selection_record_id",selection_record_id),("scope_lock_id",scope_lock_id),("repository",repository),("branch_ref",branch_ref),("evidence_policy_revision",evidence_policy_revision),("verification_matrix_revision",verification_matrix_revision),("progress_policy_revision",progress_policy_revision)): _require_nonempty(name,value)
    _require_sha(target_commit_sha); _require_digest(selection_record_digest)
    if not contract_ids or not criterion_ids: raise ScopeLockError("frozen contract and criterion selections are required")
    if not implementation_paths or not runtime_paths: raise ScopeLockError("implementation and runtime paths are required")
    if not commands: raise ScopeLockError("immutable proof commands are required")
    if len(commands) != 1: raise ScopeLockError("bounded proof requires exactly one immutable command")
    for command in commands: _validate_command(command)
    if not expected_outcomes or not evidence_destinations: raise ScopeLockError("expected outcomes and evidence destinations are required")
    if not environment_prerequisites or not stop_conditions: raise ScopeLockError("environment prerequisites and stop conditions are required")
    lock=ScopeLock(batch_id=batch_id,selection_record_id=selection_record_id,selection_record_digest=selection_record_digest.lower(),scope_lock_id=scope_lock_id,repository=repository,branch_ref=branch_ref,target_commit_sha=target_commit_sha.lower(),contract_ids=tuple(contract_ids),criterion_ids=tuple(criterion_ids),implementation_paths=tuple(implementation_paths),runtime_paths=tuple(runtime_paths),commands=tuple(commands),expected_outcomes=tuple(expected_outcomes),evidence_destinations=tuple(evidence_destinations),environment_prerequisites=tuple(environment_prerequisites),stop_conditions=tuple(stop_conditions),evidence_policy_revision=evidence_policy_revision,verification_matrix_revision=verification_matrix_revision,progress_policy_revision=progress_policy_revision,integrity_digest="")
    return replace(lock,integrity_digest=_digest(lock))

def verify_scope_lock(lock: ScopeLock) -> bool:
    if lock.status!="VALID": return False
    _require_sha(lock.target_commit_sha); _require_digest(lock.selection_record_digest)
    return lock.integrity_digest==_digest(lock)

def assert_selection_binding(lock: ScopeLock, *, selection_record_id: str, selection_record_digest: str) -> None:
    if not verify_scope_lock(lock): raise ScopeLockError("scope lock is invalid or tampered")
    _require_digest(selection_record_digest)
    if selection_record_id!=lock.selection_record_id or selection_record_digest.lower()!=lock.selection_record_digest: raise ScopeLockError("scope lock selection binding does not match frozen selection")

def invalidate_scope_lock(lock: ScopeLock, *, reason: str) -> ScopeLock:
    _require_nonempty("reason", reason)
    if not verify_scope_lock(lock):
        raise ScopeLockError("scope lock is invalid or tampered")
    if lock.status=="INVALIDATED":
        return lock
    return replace(lock,status="INVALIDATED",revision=lock.revision+1)

def assert_target_commit(lock: ScopeLock, resolved_sha: str) -> None:
    _require_sha(resolved_sha)
    if not verify_scope_lock(lock): raise ScopeLockError("scope lock is invalid or tampered")
    if resolved_sha.lower()!=lock.target_commit_sha: raise ScopeLockError("target commit does not match locked SHA")

def revise_scope_lock(lock: ScopeLock, **changes) -> ScopeLock:
    if lock.status!="INVALIDATED":
        raise ScopeLockError("scope lock must be invalidated before revision")
    immutable_scope = (
        "batch_id", "selection_record_id", "selection_record_digest",
        "repository", "branch_ref", "target_commit_sha",
        "contract_ids", "criterion_ids", "implementation_paths",
        "runtime_paths", "commands", "expected_outcomes",
        "evidence_destinations", "environment_prerequisites", "stop_conditions",
    )
    forbidden = sorted(set(changes).intersection(immutable_scope))
    if forbidden:
        raise ScopeLockError(
            "scope revision cannot mutate frozen execution scope: "
            + ", ".join(forbidden)
        )
    changes.pop("status", None)
    changes["revision"] = lock.revision + 1
    changes["status"] = "VALID"
    candidate = replace(lock, **changes, integrity_digest="")
    return replace(candidate, integrity_digest=_digest(candidate))
