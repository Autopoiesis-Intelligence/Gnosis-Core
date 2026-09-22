"""Append-only durable repository for Core diagnostic evidence."""
from __future__ import annotations

import sqlite3
from dataclasses import asdict

from gnosis.evidence.provenance import DiagnosticEvidence, canonical_digest


class DiagnosticEvidenceRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS diagnostic_evidence (
                evidence_id TEXT PRIMARY KEY,
                case_id TEXT NOT NULL,
                state_id TEXT NOT NULL,
                candidate_id TEXT NOT NULL,
                lifecycle TEXT NOT NULL,
                observations_json TEXT NOT NULL,
                provenance_refs_json TEXT NOT NULL,
                limitations_json TEXT NOT NULL,
                evidence_digest TEXT NOT NULL
            )
        """)
        self.conn.commit()

    def append(self, evidence: DiagnosticEvidence) -> None:
        import json
        payload = json.dumps(asdict(evidence), ensure_ascii=False, sort_keys=True, default=list)
        self.conn.execute(
            """INSERT INTO diagnostic_evidence
            (evidence_id,case_id,state_id,candidate_id,lifecycle,observations_json,
             provenance_refs_json,limitations_json,evidence_digest)
             VALUES (?,?,?,?,?,?,?,?,?)""",
            (evidence.evidence_id,evidence.case_id,evidence.state_id,evidence.candidate_id,
             evidence.lifecycle,json.dumps(dict(evidence.observations),sort_keys=True,default=str),
             json.dumps(evidence.provenance_refs),json.dumps(evidence.limitations),
             evidence.evidence_digest),
        )
        self.conn.commit()

    def get(self, evidence_id: str) -> DiagnosticEvidence:
        import json
        row=self.conn.execute("SELECT * FROM diagnostic_evidence WHERE evidence_id=?", (evidence_id,)).fetchone()
        if row is None: raise KeyError(evidence_id)
        return DiagnosticEvidence(row[0],row[1],row[2],row[3],row[4],json.loads(row[5]),tuple(json.loads(row[6])),tuple(json.loads(row[7])),row[8])

    def verify(self, evidence_id: str) -> bool:
        e=self.get(evidence_id)
        return e.evidence_digest == canonical_digest({
            "evidence_id":e.evidence_id,"case_id":e.case_id,"state_id":e.state_id,
            "candidate_id":e.candidate_id,"lifecycle":e.lifecycle,
            "observations":dict(e.observations),"provenance_refs":e.provenance_refs,
            "limitations":e.limitations})
