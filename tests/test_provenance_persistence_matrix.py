import sqlite3

from gnosis.core.policy import PolicyIdentity
from gnosis.evolution.provenance import build_provenance, canonical_digest
from gnosis.reflection.persistence import (
    classify_evolution_provenance,
    crosscheck_stored_provenance,
    ensure_reflection_schema,
    list_evolution_provenance,
    load_evolution_provenance,
    save_evolution_provenance,
)


def _stored_record():
    observations = {"status": "PASS"}
    policy = PolicyIdentity(
        "test-rule:default", 1, "python-source-sha256:policy-a"
    )
    provenance = build_provenance(
        candidate_id="candidate:persistence-matrix",
        parent_state_id="state:parent",
        parent_state_digest="parent-digest",
        proposed_state_digest="proposed-digest",
        observations=observations,
        evidence_digest=canonical_digest(observations),
        evaluation_status="PASS",
        shadow_status="PASS",
        invariant_status="PASS",
        governance_decision="RECORD",
        evaluated_policy=policy,
    )
    conn = sqlite3.connect(":memory:")
    ensure_reflection_schema(conn)
    save_evolution_provenance(conn, provenance)
    return conn, provenance, observations, policy


def test_evaluated_policy_survives_all_persistence_consumers():
    conn, provenance, observations, policy = _stored_record()

    loaded = load_evolution_provenance(conn, provenance.provenance_id)
    listed = list_evolution_provenance(conn, provenance.candidate_id)
    row = listed[0]
    classification = classify_evolution_provenance(row)
    crosscheck = crosscheck_stored_provenance(
        conn, provenance.provenance_id, observations=observations
    )

    assert loaded["evaluated_policy"] != ""
    assert row["evaluated_policy"] == loaded["evaluated_policy"]
    assert classification == "canonical"
    assert crosscheck.valid is True
