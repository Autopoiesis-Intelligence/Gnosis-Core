import sqlite3
import pytest
from gnosis.evolution.diagnostic_repository import DiagnosticEvidenceRepository
from gnosis.evolution.provenance import DiagnosticEvidence

def make():
    return DiagnosticEvidence("e1","case","s","c","DURABLE",{"x":1})

def test_append_and_verify():
    repo=DiagnosticEvidenceRepository(sqlite3.connect(":memory:"))
    repo.append(make())
    assert repo.get("e1").evidence_id=="e1"
    assert repo.verify("e1")

def test_repository_is_append_only():
    repo=DiagnosticEvidenceRepository(sqlite3.connect(":memory:"))
    repo.append(make())
    with pytest.raises(sqlite3.IntegrityError):
        repo.append(make())
