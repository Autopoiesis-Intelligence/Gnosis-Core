import pytest

from gnosis.storage.repositories import StorageCorruptionError, verify_audit_chain


def _disable_audit_immutability(conn):
    conn.execute("DROP TRIGGER audit_events_no_update")
    conn.execute("DROP TRIGGER audit_events_no_delete")


def test_audit_event_payload_tampering_is_rejected(persisted_transition):
    conn, _instance, _record = persisted_transition
    _disable_audit_immutability(conn)
    row = conn.execute("SELECT event_id FROM audit_events ORDER BY sequence LIMIT 1").fetchone()
    assert row is not None
    conn.execute("UPDATE audit_events SET result='tampered' WHERE event_id=?", (row[0],))
    with pytest.raises(StorageCorruptionError, match="audit event hash mismatch"):
        verify_audit_chain(conn)


def test_audit_event_hash_tampering_is_rejected(persisted_transition):
    conn, _instance, _record = persisted_transition
    _disable_audit_immutability(conn)
    row = conn.execute("SELECT event_id FROM audit_events ORDER BY sequence LIMIT 1").fetchone()
    assert row is not None
    conn.execute("UPDATE audit_events SET event_hash=? WHERE event_id=?", ("f" * 64, row[0]))
    with pytest.raises(StorageCorruptionError):
        verify_audit_chain(conn)


def test_audit_prev_hash_tampering_is_rejected(persisted_transition):
    conn, _instance, _record = persisted_transition
    _disable_audit_immutability(conn)
    rows = conn.execute("SELECT event_id FROM audit_events ORDER BY sequence").fetchall()
    assert len(rows) >= 2
    conn.execute("UPDATE audit_events SET prev_hash=? WHERE event_id=?", ("a" * 64, rows[1][0]))
    with pytest.raises(StorageCorruptionError, match="sequence/link mismatch"):
        verify_audit_chain(conn)


def test_candidate_binding_tamper_breaks_audit_record_digest():
    conn = make_connection()
    provenance = make_provenance(candidate_binding_digest="binding-original")
    result = persist_evolution_transaction(
        conn, provenance, event_type="EVOLUTION", payload={"ok": True}
    )
    row = conn.execute(
        "SELECT record_digest FROM evolution_audit WHERE sequence=?",
        (result.audit_record.sequence,),
    ).fetchone()
    original_digest = row[0]
    conn.execute(
        "UPDATE evolution_audit SET candidate_binding_digest=? WHERE sequence=?",
        ("binding-tampered", result.audit_record.sequence),
    )
    conn.commit()
    tampered = conn.execute(
        "SELECT record_digest FROM evolution_audit WHERE sequence=?",
        (result.audit_record.sequence,),
    ).fetchone()[0]
    assert tampered == original_digest
    with pytest.raises((AssertionError, ValueError, RuntimeError)):
        verify_evolution_identity_chain(conn)
