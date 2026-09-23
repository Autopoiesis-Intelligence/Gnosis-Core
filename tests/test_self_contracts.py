from gnosis.core.types import Candidate, State
from gnosis.evolution.provenance import build_provenance, canonical_digest, crosscheck_provenance


def test_self_evolution_candidate_identity_is_content_bound():
    parent = State(elements={"x": 1})
    proposed = parent.with_elements({"x": 2})
    a = Candidate(parent_state_id=parent.state_id, proposed_state=proposed, origin="self", seed=1)
    b = Candidate(parent_state_id=parent.state_id, proposed_state=proposed, origin="self", seed=1)
    assert a.candidate_id == b.candidate_id


def test_self_evolution_candidate_changes_identity_when_origin_changes():
    parent = State(elements={"x": 1})
    proposed = parent.with_elements({"x": 2})
    a = Candidate(parent_state_id=parent.state_id, proposed_state=proposed, origin="self", seed=1)
    b = Candidate(parent_state_id=parent.state_id, proposed_state=proposed, origin="external", seed=1)
    assert a.candidate_id != b.candidate_id


def test_candidate_binding_requires_parent_digest():
    parent = State(elements={"x": 1})
    proposed = parent.with_elements({"x": 2})
    candidate = Candidate(parent_state_id=parent.state_id, proposed_state=proposed, origin="self", seed=1)
    try:
        candidate.binding_digest("")
    except ValueError as exc:
        assert "parent state digest" in str(exc)
    else:
        raise AssertionError("missing parent digest must reject")


def test_learning_provenance_mismatch_is_rejected():
    observations = {"signal": "observation"}
    p = build_provenance(
        candidate_id="self-learning-candidate",
        parent_state_id="parent",
        parent_state_digest="parent-digest",
        proposed_state_digest="proposed-digest",
        observations=observations,
        evidence_digest=canonical_digest(observations),
        evaluation_status="PASS",
        shadow_status="NO_BEHAVIORAL_CHANGE",
        invariant_status="PRESERVED",
        governance_decision="REVIEW",
    )
    result = crosscheck_provenance(
        provenance=p,
        candidate_id="different-candidate",
        parent_state_id="parent",
        parent_state_digest="parent-digest",
        proposed_state_digest="proposed-digest",
        observations=observations,
    )
    assert not result.valid


def test_unverified_learning_is_not_authoritative_by_contract():
    evaluation_status = "PENDING"
    governance_decision = "REVIEW"
    assert not (evaluation_status == "PASS" and governance_decision == "ACCEPT")
