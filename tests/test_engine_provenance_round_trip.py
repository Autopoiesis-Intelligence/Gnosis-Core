import sqlite3

from gnosis.core.evolution import Engine
from gnosis.core.types import Candidate, State
from gnosis.evolution.provenance import build_provenance, canonical_digest
from gnosis.reflection.persistence import (
    crosscheck_stored_provenance,
    ensure_reflection_schema,
    load_evolution_provenance,
    save_evolution_provenance,
)


def test_engine_to_persisted_provenance_round_trip_preserves_policy_identity():
    conn = sqlite3.connect(":memory:")
    ensure_reflection_schema(conn)

    parent = State(elements={"x": 1})
    candidate = Candidate(
        parent_state_id=parent.state_id,
        proposed_state=parent.with_elements({"y": 2}),
        origin="r12-e2e-durable",
        seed=1,
    )
    engine = Engine(state=parent)
    record = engine.step(candidate)

    policy = record.policy_identity
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

    pid = save_evolution_provenance(conn, provenance)
    loaded = load_evolution_provenance(conn, pid)
    report = crosscheck_stored_provenance(
        conn, pid, observations=observations
    )

    assert loaded["provenance_id"] == provenance.provenance_id
    assert loaded["evaluated_policy"] != ""
    assert report.valid is True
