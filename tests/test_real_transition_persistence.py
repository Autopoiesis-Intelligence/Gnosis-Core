import sqlite3, hashlib, json, pytest
from gnosis.reflection.persistence import ensure_reflection_schema
from gnosis.storage.atomic_evolution import persist_evolution_with_evidence
from gnosis.core.provenance import EvidenceProvenance, canonical_digest
from gnosis.core.types import TransitionRecord, TestResult
from gnosis.core.transition_identity import transition_id

def _p(d):
    return EvidenceProvenance("p1","e1","c1","s1","pd","sd",d,"PASS","PASS","PRESERVED","COMMIT","RECORDED","ei","state","bind")

def test_persistence_uses_real_transition_record():
    conn=sqlite3.connect(":memory:"); ensure_reflection_schema(conn)
    obs={"x":1}; tr=TransitionRecord("s1","s2","c1",TestResult(False,("tested",)),False,"rejected","rule:7")
    p=_p(canonical_digest(obs))
    result=persist_evolution_with_evidence(conn,p,transition=tr,event_type="REJECT",payload={},observations=obs)
    row=conn.execute("SELECT transition_id, candidate_id, from_state_id, to_state_id, payload FROM evolution_transitions").fetchone()
    assert row[0]==transition_id(tr)
    assert row[1:4]==("c1","s1","s2")
    assert json.loads(row[4])["test_passed"] is False
    assert json.loads(row[4])["test_rule_id"]=="rule:7"

def test_transition_candidate_mismatch_rejected_before_transaction():
    conn=sqlite3.connect(":memory:"); ensure_reflection_schema(conn)
    obs={"x":1}; p=_p(canonical_digest(obs))
    tr=TransitionRecord("s1","s2","other",TestResult(True,()),True,"accepted","rule:1")
    with pytest.raises(ValueError): persist_evolution_with_evidence(conn,p,transition=tr,event_type="COMMIT",payload={},observations=obs)
    assert conn.execute("SELECT count(*) FROM evolution_transitions").fetchone()[0]==0
