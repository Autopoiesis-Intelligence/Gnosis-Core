import sqlite3

from gnosis.core.policy import PolicyIdentity
from gnosis.evolution.provenance import build_provenance, canonical_digest
from gnosis.reflection.persistence import (
    ensure_reflection_schema,
    load_evolution_provenance,
    save_evolution_provenance,
)


def test_evaluated_policy_identity_survives_provenance_persistence():
    conn = sqlite3.connect(":memory:")
    ensure_reflection_schema(conn)
    observations = {"status": "PASS"}
    policy = PolicyIdentity(
        rule_id="test-rule:default",
        rule_version=1,
        implementation_identity="python-source-sha256:policy-a",
    )
    provenance = build_provenance(
        candidate_id="candidate:r12",
        parent_state_id="state:parent",
        parent_state_digest="parent-digest",
        proposed_state_digest="proposed-digest",
        observations=observations,
        evidence_digest=canonical_digest(observations),
        evaluation_status="PASS",
        shadow_status="PASS",
        invariant_status="PASS",
        governance_decision="ACCEPT",
        candidate_binding_digest="candidate-binding",
        evaluated_policy=policy,
    )
    save_evolution_provenance(conn, provenance)
    loaded = load_evolution_provenance(conn, provenance.provenance_id)

    assert loaded["evaluated_policy"] != ""
    assert loaded["evaluated_policy"] == (
        '{"implementation_identity":"python-source-sha256:policy-a",'
        '"rule_id":"test-rule:default","rule_version":1}'
    )
