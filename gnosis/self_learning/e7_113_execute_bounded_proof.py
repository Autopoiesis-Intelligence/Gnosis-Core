"""Concrete E7.113 bounded proof execution; observe-only, no Core mutation."""
from __future__ import annotations
import json, os, shlex, subprocess, shutil
from dataclasses import asdict, dataclass
from hashlib import sha256
from enum import Enum
from pathlib import Path

from gnosis.self_learning.e7_108_execution_record import CriterionEvidence, ExecutionRecord, ExecutionState, complete
from gnosis.self_learning.e7_109_evidence_acceptance import EvidenceItem, accept_evidence
from gnosis.self_learning.e7_110_reconciliation import Metric, reconcile
from gnosis.self_learning.e7_111_independent_audit import AUDIT_CHECKS, audit_chain
from gnosis.self_learning.e7_112_immutable_closure import Closure, create_closure, verify_closure
from gnosis.self_learning.e7_113_bounded_proof_run import ProofRun, complete_proof_run, plan_proof_run
from gnosis.self_learning.e7_106_selection import SelectionRecord
from gnosis.self_learning.e7_114_preflight import assert_preflight_ready, run_preflight
from gnosis.self_learning.e7_114_scope_lock import ScopeLock, verify_scope_lock
from gnosis.self_learning.e7_114_runtime_attestation import RuntimeAttestation, attest_checkout, assert_attestation_ready

from gnosis.self_learning.e7_114_executable_attestation import ExecutableAttestation, attest_executable, verify_executable_attestation

def execute_locked_command(*, scope_lock: ScopeLock, selection_record: SelectionRecord, repository_root: str | os.PathLike[str], resolved_commit_sha: str, resolved_branch_ref: str) -> tuple[int, str, str, RuntimeAttestation, RuntimeAttestation, ExecutableAttestation]:
    root = Path(repository_root)
    report = run_preflight(scope_lock, repository_root=root, resolved_commit_sha=resolved_commit_sha, resolved_branch_ref=resolved_branch_ref, selection_record=selection_record)
    assert_preflight_ready(report)
    runtime_attestation = attest_checkout(root, scope_lock.target_commit_sha)
    assert_attestation_ready(runtime_attestation)
    if len(scope_lock.commands) != 1:
        raise ValueError("bounded proof execution requires exactly one locked command")
    if not verify_scope_lock(scope_lock):
        raise RuntimeError("scope lock changed after preflight")
    locked_command = scope_lock.commands[0]
    argv = shlex.split(locked_command)
    executable_attestation = attest_executable(argv[0], repository_root=root)
    if not verify_executable_attestation(executable_attestation):
        raise RuntimeError("resolved executable changed after attestation")
    argv[0] = executable_attestation.resolved_path
    if not argv:
        raise ValueError("locked execution command is empty")
    completed = subprocess.run(argv, cwd=root, capture_output=True, text=True, check=False)
    if not verify_executable_attestation(executable_attestation):
        raise RuntimeError("resolved executable changed after execution")
    post_runtime_attestation = attest_checkout(root, scope_lock.target_commit_sha)
    assert_attestation_ready(post_runtime_attestation)
    return completed.returncode, completed.stdout, completed.stderr, runtime_attestation, post_runtime_attestation, executable_attestation


@dataclass(frozen=True)
class BoundedProofResult:
    execution_record: ExecutionRecord
    acceptance_result: object
    reconciliation_snapshot: object
    audit_result: object
    closure: Closure
    proof_run: ProofRun

def _object_digest(value: object) -> str:
    def encode(item):
        if isinstance(item, Enum):
            return item.value
        return str(item)
    payload = json.dumps(asdict(value), sort_keys=True, separators=(",", ":"), default=encode)
    return sha256(payload.encode()).hexdigest()

def run_bounded_proof(*, run_id: str, scope_lock: ScopeLock, selection_record: SelectionRecord, repository_root: str | os.PathLike[str], resolved_commit_sha: str, resolved_branch_ref: str) -> BoundedProofResult:
    returncode, stdout, stderr, runtime_attestation, post_runtime_attestation, executable_attestation = execute_locked_command(
        scope_lock=scope_lock,
        selection_record=selection_record,
        repository_root=repository_root,
        resolved_commit_sha=resolved_commit_sha,
        resolved_branch_ref=resolved_branch_ref,
    )
    if len(scope_lock.criterion_ids) != 1 or len(scope_lock.expected_outcomes) != 1:
        raise ValueError("bounded executor requires exactly one criterion and expected outcome")
    criterion_id = scope_lock.criterion_ids[0]
    expected = scope_lock.expected_outcomes[0]
    observed = json.dumps({"returncode": returncode, "stdout": stdout, "stderr": stderr}, sort_keys=True, separators=(",", ":"))
    passed = returncode == 0
    evidence_id = sha256(observed.encode()).hexdigest()
    initial = ExecutionRecord(
        batch_id=scope_lock.batch_id,
        target_commit_sha=scope_lock.target_commit_sha,
        repository_ref=f"{scope_lock.repository}@{scope_lock.target_commit_sha}",
        environment_identity={"repository_root": str(Path(repository_root).resolve())},
        commands=scope_lock.commands,
        candidate_selection_id=selection_record.selection_record_id,
        baseline_id=selection_record.baseline_id,
        evidence_policy_revision=scope_lock.evidence_policy_revision,
        verification_matrix_revision=scope_lock.verification_matrix_revision,
        criteria=(),
        state=ExecutionState.RUNNING,
    )
    record = complete(initial, (CriterionEvidence(criterion_id, expected, observed, evidence_id, passed),))
    acceptance = accept_evidence(
        batch_id=scope_lock.batch_id,
        execution_record_id=run_id,
        items=(EvidenceItem(criterion_id, evidence_id, expected, observed, passed),),
    )
    reconciliation = reconcile(
        batch_id=scope_lock.batch_id,
        acceptance_id=run_id,
        metrics=(Metric("criterion_pass", 1.0, 1.0 if passed else 0.0),),
    )
    audit = audit_chain(
        batch_id=scope_lock.batch_id,
        target_commit_sha=scope_lock.target_commit_sha,
        record_commit_sha=scope_lock.target_commit_sha,
        execution_record=record,
        acceptance_result=acceptance,
        reconciliation_snapshot=reconciliation,
        runtime_attestation=runtime_attestation,
        post_runtime_attestation=post_runtime_attestation,
    )
    if audit.state.value != "PASSED":
        raise RuntimeError("bounded proof evidence chain failed independent audit")
    digests = tuple(_object_digest(v) for v in (record, acceptance, reconciliation, audit, runtime_attestation, post_runtime_attestation, executable_attestation))
    closure = create_closure(batch_id=scope_lock.batch_id, target_commit_sha=scope_lock.target_commit_sha, chain_digests=digests)
    if not verify_closure(closure, digests, batch_id=scope_lock.batch_id, target_commit_sha=scope_lock.target_commit_sha):
        raise RuntimeError("immutable closure verification failed")
    proof = plan_proof_run(run_id=run_id, target_commit_sha=scope_lock.target_commit_sha, mutation_authorized=False)
    proof = complete_proof_run(proof, observations=(evidence_id, closure.chain_digest), passed=passed)
    return BoundedProofResult(record, acceptance, reconciliation, audit, closure, proof)

def main() -> int:
    raise SystemExit("E7.113 execution is fail-closed: frozen SelectionRecord + ScopeLock must be supplied to execute_locked_command")

if __name__ == "__main__":
    raise SystemExit(main())
