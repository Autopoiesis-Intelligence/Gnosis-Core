"""SQLite adapter for Core recovery evidence."""
from __future__ import annotations
import sqlite3
from typing import Any
from gnosis.core.recovery import RecoveryEvidence, RecoveryPort
from gnosis.reflection.persistence import list_evolution_audit, list_evolution_provenance

class SQLiteRecoveryAdapter(RecoveryPort):
    def __init__(self, conn: sqlite3.Connection): self.conn=conn
    def load_recovery_evidence(self, provenance_id: str) -> RecoveryEvidence:
        rows=list_evolution_provenance(self.conn,candidate_id=None)
        matches=[r for r in rows if r["provenance_id"]==provenance_id]
        if not matches: raise ValueError("provenance record missing")
        row=matches[0]
        observations={}
        audits=[record.__dict__ for record in list(list_evolution_audit(self.conn))]
        return RecoveryEvidence(row,audits,observations,row.get("proposed_state_content_id",""))
