"""Canonical persisted evidence access used by recovery without depending on Research Machine persistence."""
from __future__ import annotations
import sqlite3
from gnosis.evidence.audit import EvolutionAuditRecord

def classify_evolution_provenance(row: dict) -> str:
    identity = row.get("evolution_identity")
    return "legacy_unverified" if not identity else "canonical"

def list_evolution_provenance(conn: sqlite3.Connection, candidate_id: str | None = None) -> tuple[dict, ...]:
    sql = ("SELECT provenance_id,execution_id,candidate_id,parent_state_id,parent_state_digest,proposed_state_digest,evidence_digest,"
           "evolution_identity,proposed_state_content_id,evaluation_status,shadow_status,invariant_status,governance_decision,status "
           "FROM evolution_provenance")
    params=()
    if candidate_id is not None:
        sql += " WHERE candidate_id=?"; params=(candidate_id,)
    sql += " ORDER BY rowid"
    keys=("provenance_id","execution_id","candidate_id","parent_state_id","parent_state_digest","proposed_state_digest","evidence_digest","evolution_identity","proposed_state_content_id","evaluation_status","shadow_status","invariant_status","governance_decision","status")
    return tuple(dict(zip(keys,row)) for row in conn.execute(sql,params).fetchall())

def list_evolution_audit(conn: sqlite3.Connection) -> tuple[EvolutionAuditRecord, ...]:
    rows=conn.execute("""SELECT sequence,event_type,candidate_id,execution_id,provenance_id,parent_state_digest,proposed_state_digest,evidence_digest,payload_digest,previous_digest,record_digest FROM evolution_audit ORDER BY sequence""").fetchall()
    return tuple(EvolutionAuditRecord(*row) for row in rows)
