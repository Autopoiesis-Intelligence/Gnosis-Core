import sqlite3
import pytest

from gnosis.evolution.provenance import build_provenance, canonical_digest
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
    class Conflicting:
        provenance_id = p.provenance_id
        execution_id = p.execution_id
        candidate_id = p.candidate_id
        parent_state_id = p.parent_state_id
        parent_state_digest = p.parent_state_digest
        proposed_state_digest = p.proposed_state_digest
        evidence_digest = p.evidence_digest
        evolution_identity = "evolution:tampered"
        proposed_state_content_id = "content:tampered"
        candidate_binding_digest = p.candidate_binding_digest
        evaluation_status = p.evaluation_status
        shadow_status = p.shadow_status
        invariant_status = p.invariant_status
        governance_decision = p.governance_decision
        status = p.status
    with pytest.raises(RuntimeError, match="conflicting provenance replay"):
        save_evolution_provenance(conn, Conflicting())
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
    assert not report.valid
    assert "candidate_binding_digest mismatch" in report.reasons
    conn.close()
