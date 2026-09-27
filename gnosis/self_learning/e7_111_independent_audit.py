"""E7.111 independent audit of the E7.107-E7.110 evidence chain."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from gnosis.self_learning.e7_114_runtime_attestation import verify_attestation

class AuditState(str, Enum):
    PASSED="PASSED"; REJECTED="REJECTED"; BLOCKED="BLOCKED"

@dataclass(frozen=True)
class AuditFinding:
    check_id: str
    passed: bool
    detail: str

@dataclass(frozen=True)
class AuditResult:
    batch_id: str
    target_commit_sha: str
    findings: tuple[AuditFinding,...]
    state: AuditState

AUDIT_CHECKS=(
 "exact_commit",
 "execution_identity",
 "evidence_completeness",
 "acceptance_consistency",
 "reconciliation_consistency",
 "no_conflicting_evidence",
 "terminal_state_consistency",
 "runtime_checkout_attestation",
)

def audit_chain(*, batch_id: str, target_commit_sha: str, record_commit_sha: str, execution_record, acceptance_result, reconciliation_snapshot, runtime_attestation=None) -> AuditResult:
    if not batch_id or not target_commit_sha or not record_commit_sha:
        raise ValueError("audit identity is required")

    criteria = tuple(execution_record.criteria)
    accepted_items = tuple(acceptance_result.items)
    metrics = tuple(reconciliation_snapshot.metrics)

    findings = (
        AuditFinding("exact_commit", record_commit_sha == target_commit_sha, "record commit must equal target"),
        AuditFinding("execution_identity", execution_record.batch_id == batch_id and bool(execution_record.candidate_selection_id), "execution identity"),
        AuditFinding("evidence_completeness", bool(criteria) and all(c.evidence_id and c.expected and c.observed for c in criteria), "all criteria have evidence"),
        AuditFinding("acceptance_consistency", acceptance_result.batch_id == batch_id and bool(accepted_items) and acceptance_result.state.value == "ACCEPTED" and all(i.passed for i in accepted_items), "acceptance derives from supplied evidence"),
        AuditFinding("reconciliation_consistency", reconciliation_snapshot.batch_id == batch_id and bool(metrics) and reconciliation_snapshot.state.value == "RECONCILED" and all(m.expected == m.observed for m in metrics), "reconciliation is internally consistent"),
        AuditFinding("no_conflicting_evidence", len({c.criterion_id for c in criteria}) == len(criteria) and len({i.evidence_id for i in accepted_items}) == len(accepted_items), "criterion/evidence identities are unique"),
        AuditFinding("terminal_state_consistency", execution_record.terminal and execution_record.passed, "execution must be terminal and passed"),
        AuditFinding("runtime_checkout_attestation", runtime_attestation is not None and verify_attestation(runtime_attestation) and runtime_attestation.status == "PASS" and runtime_attestation.actual_head_sha == target_commit_sha.lower(), "runtime checkout attestation must match target commit"),
    )
    state = AuditState.PASSED if all(f.passed for f in findings) else AuditState.REJECTED
    return AuditResult(batch_id, target_commit_sha, findings, state)
