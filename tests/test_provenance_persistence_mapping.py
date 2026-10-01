import sqlite3

from gnosis.core.policy import PolicyIdentity
from gnosis.evolution.provenance import build_provenance, canonical_digest
from gnosis.reflection.persistence import (
    ensure_reflection_schema,
    list_evolution_provenance,
    load_evolution_provenance,
    save_evolution_provenance,
)


def test_list_provenance_preserves_evaluated_policy_column_alignment():
    conn = sqlite3.connect(":memory:")
    ensure_reflection_schema(conn)
    observations = {"status": "PASS"}
    policy = PolicyIdentity("test-rule:default", 1, "python-source-sha256:policy-a")
    provenance = build_provenance(
        candidate_id="candidate:list-policy",
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
    save_evolution_provenance(conn, provenance)

    rows = list_evolution_provenance(conn, provenance.candidate_id)

    assert len(rows) == 1
    assert rows[0]["evaluated_policy"] == (
        '{"implementation_identity":"python-source-sha256:policy-a",'
        '"rule_id":"test-rule:default","rule_version":1}'
    )
    assert rows[0]["evaluation_status"] == "PASS"


def test_missing_provenance_id_does_not_accept_a_matching_candidate_row_as_the_requested_record():
    conn = sqlite3.connect(":memory:")
    ensure_reflection_schema(conn)
    observations = {"status": "PASS"}
    provenance = build_provenance(
        candidate_id="candidate:fallback",
        parent_state_id="state:parent",
        parent_state_digest="parent-digest",
        proposed_state_digest="proposed-digest",
        observations=observations,
        evidence_digest=canonical_digest(observations),
        evaluation_status="PASS",
        shadow_status="PASS",
        invariant_status="PASS",
        governance_decision="RECORD",
    )
    save_evolution_provenance(conn, provenance)

    try:
        load_evolution_provenance(conn, "provenance:missing")
    except KeyError as exc:
        assert str(exc) == "'provenance:missing'"
    else:
        raise AssertionError("missing provenance id must not be accepted")
