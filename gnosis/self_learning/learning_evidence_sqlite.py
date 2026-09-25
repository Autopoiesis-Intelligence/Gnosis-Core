"""R3.2 SQLite persistence/restart integration for admitted learning evidence."""
from __future__ import annotations
import json, sqlite3, subprocess, sys
from pathlib import Path

_SCHEMA = """
CREATE TABLE IF NOT EXISTS learning_evidence (
    admission_id TEXT PRIMARY KEY,
    feedback_id TEXT NOT NULL,
    verdict TEXT NOT NULL,
    learning_class TEXT NOT NULL,
    evidence_json TEXT NOT NULL
);
"""

def persist_learning_admission(conn: sqlite3.Connection, admission) -> None:
    if admission.status != "ADMITTED":
        raise ValueError("only admitted feedback may be persisted")
    conn.execute(
        "INSERT INTO learning_evidence(admission_id, feedback_id, verdict, learning_class, evidence_json) VALUES (?, ?, ?, ?, ?)",
        (admission.admission_id, admission.feedback_id, admission.verdict,
         admission.learning_class, json.dumps(admission.evidence_refs, sort_keys=True)),
    )
    conn.commit()

def load_learning_admission(conn: sqlite3.Connection, admission_id: str) -> dict:
    row = conn.execute(
        "SELECT admission_id, feedback_id, verdict, learning_class, evidence_json FROM learning_evidence WHERE admission_id=?",
        (admission_id,),
    ).fetchone()
    if row is None:
        raise KeyError(admission_id)
    return {"admission_id": row[0], "feedback_id": row[1], "verdict": row[2],
            "learning_class": row[3], "evidence_refs": tuple(json.loads(row[4]))}

def run_sqlite_restart_probe(path: Path, admission_id: str) -> dict:
    probe = f"""
import sqlite3, json
conn=sqlite3.connect(r"{path}")
row=conn.execute("SELECT admission_id, feedback_id, verdict, learning_class, evidence_json FROM learning_evidence WHERE admission_id=?", ({admission_id!r},)).fetchone()
if row is None: raise SystemExit(2)
print(json.dumps({{"admission_id":row[0],"feedback_id":row[1],"verdict":row[2],"learning_class":row[3],"evidence_refs":json.loads(row[4])}}, sort_keys=True))
conn.close()
"""
    result = subprocess.run([sys.executable, "-c", probe], check=True, capture_output=True, text=True)
    return json.loads(result.stdout)
