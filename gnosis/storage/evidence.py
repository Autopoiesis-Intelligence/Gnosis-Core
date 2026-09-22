from __future__ import annotations
import hashlib, json
import sqlite3
from typing import Any, Mapping

def _digest(v: Mapping[str, Any]) -> str:
    return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),default=str).encode()).hexdigest()

def persist_evidence(conn: sqlite3.Connection, *, execution_id: str, transition_id: str,
                     observations: Mapping[str, Any], evidence_digest: str,
                     created_payload: Mapping[str, Any] | None = None) -> str:
    digest=_digest(observations)
    if digest != evidence_digest:
        raise ValueError("evidence digest does not match observations")
    evidence_id=f"evidence:{execution_id}"
    payload=json.dumps(created_payload or {},sort_keys=True,separators=(",",":"),default=str)
    observations_json=json.dumps(observations,sort_keys=True,separators=(",",":"),default=str)
    conn.execute(
        "INSERT OR IGNORE INTO evolution_evidence(evidence_id,execution_id,transition_id,evidence_digest,observations,created_payload) VALUES(?,?,?,?,?,?)",
        (evidence_id,execution_id,transition_id,evidence_digest,observations_json,payload))
    row=conn.execute("SELECT evidence_digest,observations FROM evolution_evidence WHERE evidence_id=?",(evidence_id,)).fetchone()
    if row is None or row[0]!=evidence_digest or row[1]!=observations_json:
        raise RuntimeError("evolution evidence persistence verification failed")
    return evidence_id

def load_evidence(conn: sqlite3.Connection, execution_id: str) -> dict[str, Any]:
    row=conn.execute("SELECT evidence_id,execution_id,transition_id,evidence_digest,observations,created_payload FROM evolution_evidence WHERE execution_id=?",(execution_id,)).fetchone()
    if row is None: raise KeyError(execution_id)
    return {"evidence_id":row[0],"execution_id":row[1],"transition_id":row[2],
            "evidence_digest":row[3],"observations":json.loads(row[4]),
            "created_payload":json.loads(row[5])}
