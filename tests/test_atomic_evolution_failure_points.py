import sqlite3, pytest
from gnosis.reflection.persistence import ensure_reflection_schema
from gnosis.storage.atomic_evolution import persist_evolution_with_evidence
from gnosis.core.provenance import EvidenceProvenance, canonical_digest
from gnosis.core.types import TransitionRecord, TestResult
from gnosis.core.transition_identity import transition_id

def _p(d):
    return EvidenceProvenance("p1","e1","c1","s1","pd","sd",d,"PASS","PASS","PRESERVED","COMMIT","RECORDED","ei","state","bind")

@pytest.mark.parametrize("failure",["evidence","transition","provenance","audit","link"])
def test_atomic_graph_rolls_back_at_every_failure_point(failure):
    conn=sqlite3.connect(":memory:"); ensure_reflection_schema(conn)
    obs={"x":1}; p=_p(canonical_digest(obs))
    tr=TransitionRecord("s1","s2","c1",TestResult(True,("ok",)),True,"accepted","rule:1")
    with pytest.raises(RuntimeError):
        persist_evolution_with_evidence(conn,p,event_type="COMMIT",payload={},transition=tr,transition_id=transition_id(tr),
          observations=obs,failure_after=failure)
    for table in ("evolution_evidence","evolution_transitions","evolution_provenance","evolution_audit"):
        assert conn.execute(f"SELECT count(*) FROM {table}").fetchone()[0]==0
