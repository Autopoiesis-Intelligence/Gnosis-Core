import sqlite3

from gnosis.evidence.audit import verify_audit_chain
from gnosis.reflection.persistence import append_evolution_audit, ensure_reflection_schema, list_evolution_audit


def _db():
    conn = sqlite3.connect(":memory:")
    ensure_reflection_schema(conn)
    append_evolution_audit(conn, event_type="TEST", candidate_id="c", execution_id="e", parent_state_digest="p", proposed_state_digest="q", evidence_digest="ev", payload={"value": 1})
    append_evolution_audit(conn, event_type="TEST", candidate_id="c", execution_id="e", parent_state_digest="p2", proposed_state_digest="q2", evidence_digest="ev2", payload={"value": 2})
    return conn


def _valid(conn):
    return verify_audit_chain(list(list_evolution_audit(conn)))


def test_payload_digest_mutation_breaks_record_integrity():
    conn = _db()
    conn.execute("UPDATE evolution_audit SET payload_digest=? WHERE sequence=1", ("tampered",))
    conn.commit()
    valid, reasons = _valid(conn)
    assert not valid
    assert any("record digest mismatch" in reason for reason in reasons)


def test_record_digest_mutation_breaks_record_integrity():
    conn = _db()
    conn.execute("UPDATE evolution_audit SET record_digest=? WHERE sequence=1", ("tampered",))
    conn.commit()
    valid, _ = _valid(conn)
    assert not valid


def test_previous_link_mutation_breaks_chain():
    conn = _db()
    conn.execute("UPDATE evolution_audit SET previous_digest=? WHERE sequence=1", ("tampered",))
    conn.commit()
    valid, reasons = _valid(conn)
    assert not valid
    assert any("previous digest mismatch" in reason for reason in reasons)


def test_identity_mutation_breaks_record_integrity():
    conn = _db()
    conn.execute("UPDATE evolution_audit SET execution_id=? WHERE sequence=1", ("tampered",))
    conn.commit()
    valid, reasons = _valid(conn)
    assert not valid
    assert any("record digest mismatch" in reason for reason in reasons)
