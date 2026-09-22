import sqlite3, json, pytest
from gnosis.reflection.persistence import ensure_reflection_schema
from gnosis.storage.atomic_evolution import persist_evolution_with_evidence
from gnosis.storage.evolution_integrity import verify_evolution_integrity
from gnosis.core.provenance import EvidenceProvenance, canonical_digest
from gnosis.core.types import TransitionRecord, TestResult
from gnosis.core.transition_identity import transition_id

def setup():
    conn=sqlite3.connect(":memory:"); ensure_reflection_schema(conn)
    obs={"x":1}; p=EvidenceProvenance("p1","e1","c1","s1","pd","sd",canonical_digest(obs),"PASS","PASS","PRESERVED","COMMIT","RECORDED","ei","state","bind")
    tr=TransitionRecord("s1","s2","c1",TestResult(True,("ok",)),True,"accepted","rule:1")
    persist_evolution_with_evidence(conn,p,transition=tr,event_type="COMMIT",payload={},observations=obs)
    return conn,transition_id(tr)

def test_complete_evolution_graph_verifies():
    conn,tid=setup()
    result=verify_evolution_integrity(conn,tid)
    assert result.transition_id==tid
    assert result.provenance_id=="p1"

@pytest.mark.parametrize("table,column",[
    ("evolution_evidence","evidence_digest"),
    ("evolution_provenance","evidence_digest"),
])
def test_evolution_graph_detects_digest_divergence(table,column):
    conn,tid=setup()
    conn.execute(f"UPDATE {table} SET {column}='tampered' WHERE rowid=1")
    with pytest.raises(ValueError):
        verify_evolution_integrity(conn,tid)
