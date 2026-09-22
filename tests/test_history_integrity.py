import sqlite3, pytest
from gnosis.reflection.persistence import ensure_reflection_schema
from gnosis.storage.atomic_evolution import persist_evolution_with_evidence
from gnosis.storage.history_integrity import verify_history_integrity
from gnosis.core.provenance import EvidenceProvenance, canonical_digest
from gnosis.core.types import TransitionRecord, TestResult

def add(conn,pid,eid,from_s,to_s,prev_digest):
    obs={"id":eid}; p=EvidenceProvenance(pid,eid,"c"+eid,from_s,"pd"+eid,"sd"+eid,canonical_digest(obs),"PASS","PASS","PRESERVED","COMMIT","RECORDED","ei"+eid,"state"+eid,"bind"+eid)
    tr=TransitionRecord(from_s,to_s,"c"+eid,TestResult(True,("ok",)),True,"accepted","rule:1")
    persist_evolution_with_evidence(conn,p,transition=tr,event_type="COMMIT",payload={},observations=obs)

def test_history_integrity_accepts_single_valid_evolution():
    conn=sqlite3.connect(":memory:"); ensure_reflection_schema(conn)
    add(conn,"p1","e1","s0","s1","")
    result=verify_history_integrity(conn)
    assert result.valid

def test_history_integrity_rejects_lineage_break():
    conn=sqlite3.connect(":memory:"); ensure_reflection_schema(conn)
    add(conn,"p1","e1","s0","s1","")
    add(conn,"p2","e2","s9","s2","")
    result=verify_history_integrity(conn)
    assert not result.valid
    assert any("lineage break" in x for x in result.reasons)

def test_history_integrity_rejects_audit_tamper():
    conn=sqlite3.connect(":memory:"); ensure_reflection_schema(conn)
    add(conn,"p1","e1","s0","s1","")
    conn.execute("UPDATE evolution_audit SET record_digest='tampered' WHERE sequence=0")
    result=verify_history_integrity(conn)
    assert not result.valid
    assert any("record digest mismatch" in x for x in result.reasons)
