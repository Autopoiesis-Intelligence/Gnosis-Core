import sqlite3
import pytest
from gnosis.reflection.persistence import ensure_reflection_schema, save_evolution_provenance, append_evolution_audit
from gnosis.evolution.provenance import build_provenance, canonical_digest
from gnosis.core.types import State
from gnosis.core.state_identity import state_digest

def test_audit_append_rejects_execution_identity_mismatch():
    conn=sqlite3.connect(":memory:"); ensure_reflection_schema(conn)
    parent=State(elements={"x":1}); proposed=State(elements={"x":2}); obs={"status":"PASS"}
    p=build_provenance(candidate_id="c",parent_state_id=parent.state_id,parent_state_digest=state_digest(parent),proposed_state_digest=proposed.content_id,observations=obs,proposed_state_content_id=proposed.content_id,evidence_digest=canonical_digest(obs),evaluation_status="PASS",shadow_status="NO_BEHAVIORAL_CHANGE",invariant_status="PRESERVED",governance_decision="REVIEW")
    pid=save_evolution_provenance(conn,p)
    with pytest.raises(ValueError, match="canonical provenance"):
        append_evolution_audit(conn,event_type="PROVENANCE",candidate_id=p.candidate_id,execution_id="execution:tampered",provenance_id=pid,parent_state_digest=p.parent_state_digest,proposed_state_digest=p.proposed_state_digest,evidence_digest=p.evidence_digest,payload=obs)
