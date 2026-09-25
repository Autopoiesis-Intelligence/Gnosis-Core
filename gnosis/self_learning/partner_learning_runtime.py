"""E8.27 runtime bridge with mandatory R3.3 commit gate."""
from __future__ import annotations
from gnosis.self_learning.partner_learning_adapter import CanonicalPartnerCommitRequest, may_submit
from gnosis.self_learning.partner_learning_gate import LearningAdmission, may_commit
from gnosis.self_learning.partner_learning_persistence import PartnerLearningCommitResult, commit_partner_learning
from gnosis.self_learning.canonical_commit_guard import validate_before_canonical_commit

def commit_admitted_partner_learning(conn, *, admission: LearningAdmission, request: CanonicalPartnerCommitRequest, instance_id: str, transition_id: str, state_id: str, outcome: str, actor: str, parent_state_digest: str) -> PartnerLearningCommitResult:
    if not may_commit(admission=admission):
        raise ValueError("partner learning admission is not commit-authorized")
    if not may_submit(request=request):
        raise ValueError("partner learning request is not ready for canonical commit")
    if admission.result_id != request.result_id:
        raise ValueError("admission/request result binding mismatch")
    if admission.candidate_digest != request.provenance_digest:
        raise ValueError("admission/request provenance binding mismatch")
    if tuple(admission.evidence_refs) != tuple(request.evidence_refs):
        raise ValueError("admission/request evidence binding mismatch")
    validate_before_canonical_commit(
        parent_state_digest=parent_state_digest,
        candidate_state_digest=request.state_digest,
        evidence_verified=True,
        replay_detected=False,
    )
    return commit_partner_learning(
        conn, request_id=request.request_id, instance_id=instance_id,
        candidate_id=request.candidate_id, transition_id=transition_id,
        state_id=state_id, provenance_digest=request.provenance_digest,
        evidence=request.evidence_refs, outcome=outcome, actor=actor,
    )
