import sqlite3, pytest
from gnosis.reflection.persistence import ensure_reflection_schema
from gnosis.storage.atomic_evolution import persist_evolution_with_evidence
from gnosis.storage.recovery_checkpoint import build_recovery_checkpoint
from gnosis.core.provenance import EvidenceProvenance, canonical_digest
from gnosis.core.types import TransitionRecord, TestResult
from gnosis.core.transition_identity import transition_id

def setup():
    conn=sqlite3.connect(":memory:"); ensure_reflection_schema(conn)
    conn.execute("CREATE TABLE evolution_current_state(state_id TEXT NOT NULL,state_digest TEXT NOT NULL)")
    obs={"x":1}; p=EvidenceProvenance("p1","e1","c1","s0","pd","s1",canonical_digest(obs),"PASS","PASS","PRESERVED","COMMIT","RECORDED","ei","state","bind")
    tr=TransitionRecord("s0","s1","c1",TestResult(True,("ok",)),True,"accepted","rule:1")
    persist_evolution_with_evidence(conn,p,transition=tr,event_type="COMMIT",payload={},observations=obs)
    conn.execute("INSERT INTO evolution_current_state VALUES(?,?)",("s1","digest:s1"))
    return conn,tr

def test_checkpoint_binds_state_and_audit():
    conn,tr=setup(); cp=build_recovery_checkpoint(conn)
    assert cp.transition_id==transition_id(tr)
    assert cp.state_id=="s1"
    assert cp.audit_sequence==0

def test_checkpoint_rejects_wrong_current_state():
    conn,_=setup(); conn.execute("UPDATE evolution_current_state SET state_id='tampered'")
    with pytest.raises(ValueError,match="state lineage"):
        build_recovery_checkpoint(conn)
