from gnosis.core.evolution import Engine
from gnosis.core.types import Candidate, State
from gnosis.evolution.provenance import build_provenance, canonical_digest


def test_engine_transition_carries_authorized_policy_into_provenance():
    parent = State(elements={"x": 1})
    candidate = Candidate(
        parent_state_id=parent.state_id,
        proposed_state=parent.with_elements({"y": 2}),
        origin="r12-e2e",
        seed=1,
    )
    engine = Engine(state=parent)
    record = engine.step(candidate)

    policy = record.policy_identity
    assert policy == engine.policy_binding.policy

    observations = {"transition_id": record.transition_id}
    provenance = build_provenance(
        candidate_id=record.candidate_id,
        parent_state_id=record.from_state_id,
        parent_state_digest=parent.state_id,
        proposed_state_digest=candidate.proposed_state.state_id,
        proposed_state_content_id=candidate.proposed_state.content_id,
        candidate_binding_digest=candidate.binding_digest(parent.state_id),
        observations=observations,
        evidence_digest=canonical_digest(observations),
        evaluation_status="PASS" if record.accepted else "REJECTED",
        shadow_status="PASS",
        invariant_status="PASS",
        governance_decision="RECORD",
        evaluated_policy=policy,
    )

    assert provenance.evaluated_policy == engine.policy_binding.policy
    assert provenance.candidate_binding_digest == candidate.binding_digest(parent.state_id)
