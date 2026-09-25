from pathlib import Path
import sqlite3

from gnosis.self_learning.feedback_integration import admit_feedback
from gnosis.self_learning.learning_evidence_sqlite import (
    _SCHEMA,
    load_learning_admission,
    persist_learning_admission,
    run_sqlite_restart_probe,
)

def test_r32_learning_influence_survives_sqlite_restart(tmp_path: Path):
    path = tmp_path / "learning.sqlite"
    conn = sqlite3.connect(path)
    conn.executescript(_SCHEMA)
    admission = admit_feedback(
        feedback_id="feedback:cycle-1",
        contract_id="contract:e806",
        scope="sandbox",
        verdict="FAIL",
        evidence_refs=("evidence:failure-1",),
        learning_class="COUNTEREXAMPLE",
        status="ADMITTED",
    )
    persist_learning_admission(conn, admission)
    conn.close()

    recovered = run_sqlite_restart_probe(path, admission.admission_id)
    assert recovered["admission_id"] == admission.admission_id
    assert recovered["evidence_refs"] == ["evidence:failure-1"]
    assert recovered["learning_class"] == "COUNTEREXAMPLE"

    reopened = sqlite3.connect(path)
    assert load_learning_admission(reopened, admission.admission_id)["evidence_refs"] == (
        "evidence:failure-1",
    )
    reopened.close()

def test_r32_unadmitted_feedback_cannot_be_persisted(tmp_path: Path):
    path = tmp_path / "blocked.sqlite"
    conn = sqlite3.connect(path)
    conn.executescript(_SCHEMA)
    admission = admit_feedback(
        feedback_id="feedback:blocked",
        contract_id="contract:e806",
        scope="sandbox",
        verdict="FAIL",
        evidence_refs=("evidence:failure",),
        learning_class="COUNTEREXAMPLE",
        status="PROPOSED",
    )
    try:
        persist_learning_admission(conn, admission)
    except ValueError:
        pass
    else:
        raise AssertionError("unadmitted feedback crossed persistence boundary")
