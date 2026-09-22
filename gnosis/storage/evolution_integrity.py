"""Independent integrity verification for one durable evolution graph."""
from __future__ import annotations
import json, sqlite3
from dataclasses import dataclass
from gnosis.core.types import TransitionRecord, TestResult
from gnosis.core.transition_identity import transition_id

@dataclass(frozen=True)
class EvolutionIntegrity:
    transition_id: str
    evidence_digest: str
    provenance_id: str
    audit_record_id: str

def verify_evolution_integrity(conn: sqlite3.Connection, tid: str) -> EvolutionIntegrity:
    t=conn.execute("SELECT transition_id,candidate_id,from_state_id,to_state_id,provenance_id,audit_record_id,evidence_digest,payload FROM evolution_transitions WHERE transition_id=?",(tid,)).fetchone()
    if t is None: raise KeyError(tid)
    p=json.loads(t[7])
    record=TransitionRecord(t[2],t[3],t[1],TestResult(bool(p["test_passed"]),tuple(p.get("test_reasons",()))),bool(p["accepted"]),p["reason"],p.get("test_rule_id"))
    if transition_id(record)!=t[0]: raise ValueError("transition identity mismatch")
    e=conn.execute("SELECT evidence_digest,transition_id FROM evolution_evidence WHERE evidence_id=?",(f"evidence:{conn.execute('SELECT execution_id FROM evolution_provenance WHERE provenance_id=?',(t[4],)).fetchone()[0]}",)).fetchone()
    if e is None or e[0]!=t[6] or e[1]!=t[0]: raise ValueError("evidence linkage mismatch")
    pr=conn.execute("SELECT execution_id,candidate_id,evidence_digest FROM evolution_provenance WHERE provenance_id=?",(t[4],)).fetchone()
    if pr is None or pr[1]!=t[1] or pr[2]!=t[6]: raise ValueError("provenance linkage mismatch")
    a=conn.execute("SELECT record_digest,provenance_id,evidence_digest FROM evolution_audit WHERE record_digest=?",(t[5],)).fetchone()
    if a is None or a[1]!=t[4] or a[2]!=t[6]: raise ValueError("audit linkage mismatch")
    return EvolutionIntegrity(t[0],t[6],t[4],t[5])
