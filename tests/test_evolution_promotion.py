from gnosis.evolution.promotion import (
    evaluate_promotion_gate,
    make_promotion_candidate,
)


def test_verified_learning_proposal_may_become_eligible_but_not_authoritative():
    candidate = make_promotion_candidate(
        candidate_id="learning:candidate:verified",
        evidence_digest="evidence:1",
        evaluation_status="PASS",
        shadow_status="IMPROVED",
        invariant_status="PRESERVED",
        governance_decision="APPROVE",
    )
    gate = evaluate_promotion_gate(
        candidate,
        provenance_valid=True,
        required_evidence=("evidence:1",),
    )
    assert gate.eligible is True
    assert gate.can_activate is False
    assert candidate.can_activate is False


def test_learning_proposal_cannot_become_eligible_without_verified_shadow():
    candidate = make_promotion_candidate(
        candidate_id="learning:candidate:shadow-fail",
        evidence_digest="evidence:2",
        evaluation_status="PASS",
        shadow_status="BEHAVIOR_CHANGED",
        invariant_status="PRESERVED",
        governance_decision="APPROVE",
    )
    gate = evaluate_promotion_gate(
        candidate,
        provenance_valid=True,
        required_evidence=("evidence:2",),
    )
    assert gate.eligible is False
    assert "shadow result is not acceptable" in gate.reasons
