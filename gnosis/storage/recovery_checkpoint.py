"""Canonical restart checkpoint for verified evolution recovery."""
from __future__ import annotations
import sqlite3
from dataclasses import dataclass
from gnosis.storage.lineage_recovery import reconstruct_lineage
from gnosis.storage.evolution_integrity import verify_evolution_integrity

@dataclass(frozen=True)
class RecoveryCheckpoint:
    transition_id: str | None
    state_id: str
    audit_sequence: int | None
    state_digest: str | None

def build_recovery_checkpoint(conn: sqlite3.Connection) -> RecoveryCheckpoint:
    lineage=reconstruct_lineage(conn)
    if not lineage:
        row=conn.execute("SELECT state_id,state_digest FROM evolution_current_state LIMIT 1").fetchone()
        if row is None: raise ValueError("no recovery state")
        return RecoveryCheckpoint(None,row[0],None,row[1])
    last=lineage[-1]
    integrity=verify_evolution_integrity(conn,last.transition_id)
    row=conn.execute("SELECT sequence FROM evolution_audit WHERE record_digest=?",(integrity.audit_record_id,)).fetchone()
    if row is None: raise ValueError("checkpoint audit record missing")
    state=conn.execute("SELECT state_id,state_digest FROM evolution_current_state LIMIT 1").fetchone()
    if state is None: raise ValueError("current state missing")
    if state[0] != last.to_state_id: raise ValueError("checkpoint state lineage mismatch")
    return RecoveryCheckpoint(last.transition_id,state[0],row[0],state[1])
