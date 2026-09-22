"""History-level recovery integrity: lineage continuity plus audit chain."""
from __future__ import annotations
import sqlite3
from dataclasses import dataclass
from gnosis.core.audit import EvolutionAuditRecord, verify_audit_chain
from gnosis.storage.evolution_integrity import verify_evolution_integrity

@dataclass(frozen=True)
class HistoryIntegrity:
    valid: bool
    reasons: tuple[str, ...]

def verify_history_integrity(conn: sqlite3.Connection) -> HistoryIntegrity:
    reasons=[]
    rows=conn.execute("SELECT sequence,event_type,candidate_id,execution_id,provenance_id,parent_state_digest,proposed_state_digest,evidence_digest,payload_digest,previous_digest,record_digest FROM evolution_audit ORDER BY sequence").fetchall()
    records=[EvolutionAuditRecord(*r) for r in rows]
    ok,audit_reasons=verify_audit_chain(records)
    if not ok: reasons.extend(audit_reasons)
    transitions=conn.execute("SELECT transition_id,from_state_id,to_state_id FROM evolution_transitions ORDER BY rowid").fetchall()
    previous_to=None
    for tid,from_state,to_state in transitions:
        if previous_to is not None and from_state!=previous_to:
            reasons.append(f"transition lineage break before {tid}")
        try: verify_evolution_integrity(conn,tid)
        except Exception as exc: reasons.append(f"{tid}: {exc}")
        previous_to=to_state
    return HistoryIntegrity(not reasons,tuple(dict.fromkeys(reasons)))
