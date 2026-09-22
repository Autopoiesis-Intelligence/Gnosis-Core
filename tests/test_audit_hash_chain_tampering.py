import sqlite3
import pytest

from gnosis.reflection.persistence import ensure_reflection_schema, append_evolution_audit, verify_evolution_audit


def _db():
    conn=sqlite3.connect(":memory:")
    ensure_reflection_schema(conn)
    append_evolution_audit(conn,event_type="TEST",candidate_id="c",execution_id="e",provenance_id=None,parent_state_digest="p",proposed_state_digest="q",evidence_digest="ev",payload={"value":1})
    append_evolution_audit(conn,event_type="TEST",candidate_id="c",execution_id="e",provenance_id=None,parent_state_digest="p2",proposed_state_digest="q2",evidence_digest="ev2",payload={"value":2})
    return conn


def test_payload_mutation_breaks_audit_integrity():
    conn=_db(); conn.execute("UPDATE evolution_audit SET payload_json=? WHERE sequence=1", ('{"value":999}',)); conn.commit()
    assert not verify_evolution_audit(conn)


def test_payload_digest_mutation_breaks_record_integrity():
    conn=_db(); conn.execute("UPDATE evolution_audit SET payload_digest=? WHERE sequence=1", ("tampered",)); conn.commit()
    assert not verify_evolution_audit(conn)


def test_record_digest_mutation_breaks_record_integrity():
    conn=_db(); conn.execute("UPDATE evolution_audit SET record_digest=? WHERE sequence=1", ("tampered",)); conn.commit()
    assert not verify_evolution_audit(conn)


def test_previous_link_mutation_breaks_chain():
    conn=_db(); conn.execute("UPDATE evolution_audit SET previous_digest=? WHERE sequence=2", ("tampered",)); conn.commit()
    assert not verify_evolution_audit(conn)
