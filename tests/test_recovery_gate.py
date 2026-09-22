import sqlite3, pytest
from gnosis.reflection.persistence import ensure_reflection_schema
from gnosis.storage.atomic_evolution import persist_evolution_with_evidence
from gnosis.storage.recovery_gate import recovery_pre_resume_gate
from gnosis.core.provenance import EvidenceProvenance, canonical_digest
from gnosis.core.types import TransitionRecord, TestResult
from gnosis.core.transition_identity import transition_id

def setup():
    conn=sqlite3.connect(":memory:"); ensure_reflection_schema(conn)
    obs={"x":1}; p=EvidenceProvenance("p1","e1","c1","s1","pd","sd",canonical_digest(obs),"PASS","PASS","PRESERVED","COMMIT","RECORDED","ei","state","bind")
    tr=TransitionRecord("s1","s2","c1",TestResult(True,("ok",)),True,"accepted","rule:1")
    persist_evolution_with_evidence(conn,p,transition=tr,event_type="COMMIT",payload={},observations=obs)
    return conn,transition_id(tr)

def test_recovery_gate_allows_only_intact_graph():
    conn,tid=setup()
    gate=recovery_pre_resume_gate(conn,tid)
    assert gate.allowed is True
    assert gate.integrity is not None

@pytest.mark.parametrize("sql",[
    "UPDATE evolution_evidence SET evidence_digest='bad' WHERE rowid=1",
    "UPDATE evolution_provenance SET evidence_digest='bad' WHERE rowid=1",
])
def test_recovery_gate_hard_stops_corruption(sql):
    conn,tid=setup(); conn.execute(sql)
    gate=recovery_pre_resume_gate(conn,tid)
    assert gate.allowed is False
    assert gate.integrity is None
    assert gate.reason
