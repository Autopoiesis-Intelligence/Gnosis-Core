import sqlite3

from gnosis.core.policy import PolicyIdentity
from gnosis.evolution.provenance import build_provenance, canonical_digest
from gnosis.reflection.persistence import (
    crosscheck_stored_provenance,
    ensure_reflection_schema,
    load_evolution_provenance,
    save_evolution_provenance,
)


def _provenance():
    observations = {"status": "PASS"}
    policy = PolicyIdentity(
        rule_id="test-rule:default",
        rule_version=1,
        implementation_identity="python-source-sha256:policy-a",
    )
    return build_provenance(
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
    ), observations


def test_evaluated_policy_identity_survives_provenance_persistence():
    conn = sqlite3.connect(":memory:")
    ensure_reflection_schema(conn)
    provenance, _ = _provenance()
    save_evolution_provenance(conn, provenance)
    loaded = load_evolution_provenance(conn, provenance.provenance_id)

    assert loaded["evaluated_policy"] == (
        '{"implementation_identity":"python-source-sha256:policy-a",'
        '"rule_id":"test-rule:default","rule_version":1}'
    )


def test_reloaded_evaluated_policy_revalidates_provenance_identity():
    conn = sqlite3.connect(":memory:")
    ensure_reflection_schema(conn)
    provenance, observations = _provenance()
    save_evolution_provenance(conn, provenance)

    report = crosscheck_stored_provenance(
        conn, provenance.provenance_id, observations=observations
    )

    assert report.valid is True


def test_tampered_persisted_policy_identity_is_rejected():
    conn = sqlite3.connect(":memory:")
    ensure_reflection_schema(conn)
    provenance, observations = _provenance()
    save_evolution_provenance(conn, provenance)

    conn.execute(
        "UPDATE evolution_provenance SET evaluated_policy=? WHERE provenance_id=?",
        (
            '{"implementation_identity":"python-source-sha256:tampered",'
            '"rule_id":"test-rule:default","rule_version":1}',
            provenance.provenance_id,
        ),
    )
    conn.commit()

    report = crosscheck_stored_provenance(
        conn, provenance.provenance_id, observations=observations
    )

    assert report.valid is False
    assert "stored provenance identity mismatch" in report.reasons
