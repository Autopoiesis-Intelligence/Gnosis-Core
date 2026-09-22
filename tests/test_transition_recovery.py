import sqlite3, json, pytest
from gnosis.reflection.persistence import ensure_reflection_schema
from gnosis.storage.atomic_evolution import persist_evolution_with_evidence
from gnosis.storage.transition_recovery import load_transition
from gnosis.core.provenance import EvidenceProvenance, canonical_digest
from gnosis.core.types import TransitionRecord, TestResult
from gnosis.core.transition_identity import transition_id

def test_recovery_reconstructs_exact_transition():
    conn=sqlite3.connect(":memory:"); ensure_reflection_schema(conn)
    obs={"x":1}; p=EvidenceProvenance("p1","e1","c1","s1","pd","sd",canonical_digest(obs),"PASS","PASS","PRESERVED","COMMIT","RECORDED","ei","state","bind")
    tr=TransitionRecord("s1","s2","c1",TestResult(False,("tested",)),False,"rejected","rule:7")
    persist_evolution_with_evidence(conn,p,transition=tr,event_type="REJECT",payload={},observations=obs)
    assert load_transition(conn,transition_id(tr)) == tr

def test_recovery_detects_transition_tampering():
    conn=sqlite3.connect(":memory:"); ensure_reflection_schema(conn)
    obs={"x":1}; p=EvidenceProvenance("p1","e1","c1","s1","pd","sd",canonical_digest(obs),"PASS","PASS","PRESERVED","COMMIT","RECORDED","ei","state","bind")
    tr=TransitionRecord("s1","s2","c1",TestResult(True,("ok",)),True,"accepted","rule:1")
    persist_evolution_with_evidence(conn,p,transition=tr,event_type="COMMIT",payload={},observations=obs)
    tid=transition_id(tr)
    row=conn.execute("SELECT payload FROM evolution_transitions WHERE transition_id=?",(tid,)).fetchone()
    payload=json.loads(row[0]); payload["to_state_id"]="tampered"
    conn.execute("UPDATE evolution_transitions SET payload=? WHERE transition_id=?",(json.dumps(payload,sort_keys=True,separators=(",",":")),tid))
    with pytest.raises(ValueError, match="identity mismatch"):
        load_transition(conn,tid)
