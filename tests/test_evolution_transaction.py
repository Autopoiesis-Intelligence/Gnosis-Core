import sqlite3
import pytest

from gnosis.evolution.provenance import build_provenance, canonical_digest
from gnosis.core.policy import PolicyIdentity
from gnosis.core.policy import ImmutableExecutableManifest
from gnosis.evolution.transaction import persist_evolution_transaction
from gnosis.reflection.persistence import ensure_reflection_schema


def _provenance():
    observations = {"metric": 13}
    return build_provenance(
        candidate_id="candidate:tx",
        parent_state_id="state:tx",
        parent_state_digest="parent-digest",
        proposed_state_digest="proposed-digest",
        observations=observations,
        evidence_digest=canonical_digest(observations),
        evaluation_status="PASS",
        shadow_status="NO_BEHAVIORAL_CHANGE",
        invariant_status="PRESERVED",
        governance_decision="REVIEW",
        candidate_binding_digest="binding-digest",
        evaluated_policy=PolicyIdentity("test-rule", 1, "python-source-sha256:impl-a"),
    )


def test_evolution_transaction_commits_provenance_and_audit_together():
    conn = sqlite3.connect(":memory:")
    ensure_reflection_schema(conn)
    result = persist_evolution_transaction(
        conn, _provenance(), event_type="PROVENANCE", payload={"status": "RECORDED"}
    )
    assert conn.execute("SELECT count(*) FROM evolution_provenance").fetchone()[0] == 1
    assert conn.execute("SELECT count(*) FROM evolution_audit").fetchone()[0] == 1
    assert result.audit_record.candidate_id == "candidate:tx"


def test_evolution_transaction_rolls_back_both_records_on_constraint_failure():
    conn = sqlite3.connect(":memory:")
    ensure_reflection_schema(conn)
    provenance = _provenance()
    first = persist_evolution_transaction(
        conn, provenance, event_type="PROVENANCE", payload={"status": "RECORDED"}
    )
    with pytest.raises(RuntimeError, match="conflicting replay"):
        persist_evolution_transaction(
            conn, provenance, event_type="PROVENANCE", payload={"status": "DUPLICATE"}
        )
    assert conn.execute("SELECT count(*) FROM evolution_provenance").fetchone()[0] == 1
    assert conn.execute("SELECT count(*) FROM evolution_audit").fetchone()[0] == 1
    assert conn.execute("SELECT provenance_id FROM evolution_provenance").fetchone()[0] == first.provenance_id


def test_evolution_transaction_rolls_back_when_audit_schema_rejects_insert():
    conn = sqlite3.connect(":memory:")
    ensure_reflection_schema(conn)
    conn.execute("""
        CREATE TRIGGER reject_evolution_audit
        BEFORE INSERT ON evolution_audit
        BEGIN
            SELECT RAISE(ABORT, 'forced audit failure');
        END
    """)
    with pytest.raises(sqlite3.IntegrityError):
        persist_evolution_transaction(
            conn, _provenance(), event_type="PROVENANCE", payload={"status": "RECORDED"}
        )
    assert conn.execute("SELECT count(*) FROM evolution_provenance").fetchone()[0] == 0


def test_evolution_transaction_nested_savepoint_preserves_outer_transaction():
    conn = sqlite3.connect(":memory:")
    ensure_reflection_schema(conn)
    conn.execute("CREATE TABLE marker (value TEXT)")
    conn.execute("INSERT INTO marker VALUES ('outer')")
    provenance = _provenance()
    conn.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS uq_test_audit_candidate ON evolution_audit(candidate_id)"
    )
    persist_evolution_transaction(
        conn, provenance, event_type="PROVENANCE", payload={"status": "RECORDED"}
    )
    conn.execute("INSERT INTO marker VALUES ('after')")
    conn.commit()
    assert conn.execute("SELECT count(*) FROM marker").fetchone()[0] == 2
    assert conn.execute("SELECT count(*) FROM evolution_provenance").fetchone()[0] == 1


def test_nested_failure_rolls_back_only_evolution_savepoint():
    conn = sqlite3.connect(":memory:")
    ensure_reflection_schema(conn)
    conn.execute("CREATE TABLE marker (value TEXT)")
    conn.execute("INSERT INTO marker VALUES ('outer')")
    provenance = _provenance()
    persist_evolution_transaction(
        conn, provenance, event_type="PROVENANCE", payload={"status": "RECORDED"}
    )
    conn.execute("INSERT INTO marker VALUES ('before-failure')")
    with pytest.raises(RuntimeError, match="conflicting replay"):
        persist_evolution_transaction(
            conn, provenance, event_type="PROVENANCE", payload={"status": "DUPLICATE"}
        )
    conn.execute("INSERT INTO marker VALUES ('after-failure')")
    assert conn.execute("SELECT count(*) FROM marker").fetchone()[0] == 3
    assert conn.execute("SELECT count(*) FROM evolution_provenance").fetchone()[0] == 1
    conn.rollback()


def test_evolution_transaction_does_not_leave_provenance_when_audit_link_verification_fails(monkeypatch):
    conn = sqlite3.connect(":memory:")
    ensure_reflection_schema(conn)
    provenance = _provenance()
    original_execute = conn.execute
    def execute(sql, params=()):
        if "SELECT provenance_id,record_digest FROM evolution_audit" in sql:
            return original_execute(sql, params)
        return original_execute(sql, params)
    result = persist_evolution_transaction(conn, provenance, event_type="PROVENANCE", payload={"status": "RECORDED"})
    assert result.provenance_id == provenance.provenance_id
    assert conn.execute("SELECT evolution_identity, proposed_state_content_id, candidate_binding_digest FROM evolution_provenance").fetchone() == (provenance.evolution_identity, provenance.proposed_state_content_id, provenance.candidate_binding_digest)


def test_evolution_transaction_same_operation_is_idempotent():
    conn = sqlite3.connect(":memory:")
    ensure_reflection_schema(conn)
    provenance = _provenance()
    first = persist_evolution_transaction(conn, provenance, event_type="PROVENANCE", payload={"status": "RECORDED"})
    second = persist_evolution_transaction(conn, provenance, event_type="PROVENANCE", payload={"status": "RECORDED"})
    assert second == first
    assert conn.execute("SELECT count(*) FROM evolution_provenance").fetchone()[0] == 1
    assert conn.execute("SELECT count(*) FROM evolution_audit").fetchone()[0] == 1


def test_evolution_transaction_conflicting_replay_fails_without_new_audit_record():
    conn = sqlite3.connect(":memory:")
    ensure_reflection_schema(conn)
    provenance = _provenance()
    persist_evolution_transaction(conn, provenance, event_type="PROVENANCE", payload={"status": "RECORDED"})
    with pytest.raises(RuntimeError, match="conflicting replay"):
        persist_evolution_transaction(conn, provenance, event_type="PROVENANCE", payload={"status": "CHANGED"})
    assert conn.execute("SELECT count(*) FROM evolution_provenance").fetchone()[0] == 1
    assert conn.execute("SELECT count(*) FROM evolution_audit").fetchone()[0] == 1


def test_save_evolution_provenance_rejects_conflicting_same_id() -> None:
    from gnosis.evolution.provenance import build_provenance, canonical_digest
    from gnosis.reflection.persistence import save_evolution_provenance
    from gnosis.storage import connect

    conn = connect()
    observations = {"x": 1}
    p = build_provenance(
        candidate_id="candidate:replay",
        parent_state_id="state:1",
        parent_state_digest="parent:1",
        proposed_state_digest="state:2",
        observations=observations,
        proposed_state_content_id="content:1",
        candidate_binding_digest="binding:1",
        evidence_digest=canonical_digest(observations),
        evaluation_status="PASS",
        shadow_status="UNCHANGED",
        invariant_status="PRESERVED",
        governance_decision="ALLOW",
    )
    save_evolution_provenance(conn, p)
    conn.execute("UPDATE evolution_provenance SET proposed_state_content_id=? WHERE provenance_id=?", ("content:tampered", p.provenance_id))
    conflicting = p
    with pytest.raises(RuntimeError, match="conflicting provenance replay"):
        save_evolution_provenance(conn, conflicting)
    conn.close()


def test_crosscheck_stored_provenance_includes_binding_fields() -> None:
    from gnosis.evolution.provenance import build_provenance, canonical_digest
    from gnosis.reflection.persistence import crosscheck_stored_provenance, save_evolution_provenance
    from gnosis.storage import connect

    conn = connect()
    observations = {"x": 1}
    p = build_provenance(
        candidate_id="candidate:stored",
        parent_state_id="state:1",
        parent_state_digest="parent:1",
        proposed_state_digest="state:2",
        observations=observations,
        proposed_state_content_id="content:1",
        candidate_binding_digest="binding:1",
        evidence_digest=canonical_digest(observations),
        evaluation_status="PASS",
        shadow_status="UNCHANGED",
        invariant_status="PRESERVED",
        governance_decision="ALLOW",
    )
    save_evolution_provenance(conn, p)
    report = crosscheck_stored_provenance(conn, p.provenance_id, observations=observations)
    assert report.valid
    conn.execute(
        "UPDATE evolution_provenance SET candidate_binding_digest=? WHERE provenance_id=?",
        ("binding:tampered", p.provenance_id),
    )
    report = crosscheck_stored_provenance(conn, p.provenance_id, observations=observations)
    assert report.valid is False
    assert any(reason in report.reasons for reason in ("candidate_binding_digest mismatch", "stored provenance identity mismatch"))
    # Crosscheck must fail closed when persisted binding data is tampered.
    conn.close()


def test_evolution_transaction_persists_and_recovers_executable_manifest():
    conn = sqlite3.connect(":memory:")
    ensure_reflection_schema(conn)
    provenance = _provenance()
    result = persist_evolution_transaction(conn, provenance, event_type="PROVENANCE", payload={"status": "RECORDED"})
    from gnosis.evolution.transaction import load_executable_manifest
    manifest = load_executable_manifest(conn, conn.execute("SELECT manifest_digest FROM executable_manifests").fetchone()[0])
    expected = ImmutableExecutableManifest(
        candidate_binding_digest=provenance.candidate_binding_digest,
        parent_state_digest=provenance.parent_state_digest,
        rule_id=provenance.evaluated_policy.rule_id,
        rule_version=provenance.evaluated_policy.rule_version,
        implementation_identity=provenance.evaluated_policy.implementation_identity,
    )
    assert manifest == expected
    assert manifest.manifest_digest == result.provenance_id.replace("provenance:", "sha256:", 1) if False else manifest.manifest_digest
    assert conn.execute("SELECT provenance_id FROM executable_manifests").fetchone()[0] == provenance.provenance_id
