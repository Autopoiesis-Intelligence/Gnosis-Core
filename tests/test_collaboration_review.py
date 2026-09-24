import pytest
from dataclasses import FrozenInstanceError, replace
from gnosis.self_learning.collaboration_proposal import generate_collaboration_proposal
from gnosis.self_learning.collaboration_review import review_collaboration_proposal, review_record_valid

def proposal():
    return generate_collaboration_proposal(
        contract_id="sha256:contract", channel="COMMERCIAL", title="Bounded",
        objective="specialization", scope="partner:demo",
        evidence_refs=("evidence:1",), requested_inputs=("brief",),
        deliverable_contract_refs=("E7.74",), publication_target="github:proposal",
        revision="r1",
    )

def review(decision="ACCEPTED", **kw):
    return review_collaboration_proposal(
        proposal=proposal(), generator_revision="generator:r1",
        contract_refs=("E7.74:r1",), reviewer_id="owner:1",
        review_reason=kw.pop("reason", "reviewed"), evidence_id="evidence:review:1",
        decision=decision, resulting_revision=kw.pop("resulting_revision", "r1"), **kw
    )

def test_all_decisions_are_explicit():
    assert {review(d).decision for d in ("ACCEPTED","REJECTED","DEFERRED")} == {"ACCEPTED","REJECTED","DEFERRED"}
    assert review("RETURNED_FOR_REVISION", resulting_revision="r2").decision == "RETURNED_FOR_REVISION"

def test_acceptance_is_not_execution_authorization():
    r = review()
    assert r.decision == "ACCEPTED"
    assert r.status == "ACCEPTED"

def test_acceptance_requires_dependencies_authority_and_freshness():
    for kw in ({"dependencies_present":False},{"reviewer_authorized":False},{"stale":True},{"revoked":True},{"scope_expanding":True}):
        with pytest.raises(ValueError): review(**kw)

def test_private_data_blocks_acceptance():
    with pytest.raises(ValueError):
        review(private_data_refs=("secret:1",))

def test_revision_return_requires_new_revision():
    with pytest.raises(ValueError): review("RETURNED_FOR_REVISION", resulting_revision="r1")

def test_replay_is_deterministic():
    assert review() == review()

def test_review_binds_exact_proposal_revision():
    r = review()
    assert review_record_valid(record=r, proposal=proposal(), current_revision="r1")
    assert not review_record_valid(record=r, proposal=proposal(), current_revision="r2")

def test_tampering_breaks_identity():
    r = review()
    with pytest.raises(ValueError):
        replace(r, decision="REJECTED")

def test_review_record_is_immutable():
    with pytest.raises(FrozenInstanceError):
        review().decision = "REJECTED"

def test_rejection_and_deferral_require_reason():
    with pytest.raises(ValueError): review("REJECTED", reason="")
    with pytest.raises(ValueError): review("DEFERRED", reason="")

def test_conflicting_replay_has_distinct_identity():
    assert review("REJECTED") .review_id != review("DEFERRED").review_id
