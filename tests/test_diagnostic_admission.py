import pytest
from gnosis.evolution.diagnostic_admission import DiagnosticEvidenceAdmission
from gnosis.evolution.evaluator import EvaluationResult
from gnosis.evolution.provenance import DiagnosticEvidence
from gnosis.evolution.replay import ReplayResult

def base():
    return DiagnosticEvidence("e","case","s","c","EPHEMERAL",{"x":1})

def test_admission_is_fail_closed_and_ordered():
    a=DiagnosticEvidenceAdmission(); e=a.admit_observed(base())
    with pytest.raises(ValueError): a.admit_verified(e, ReplayResult(True,()), EvaluationResult("PASS",(),e.evidence_digest))
    e=a.admit_reproduced(e, ReplayResult(True,()))
    e=a.admit_verified(e, ReplayResult(True,()), EvaluationResult("PASS",(),e.evidence_digest))
    assert a.admit_durable(e).lifecycle=="DURABLE"

def test_failed_replay_cannot_verify():
    a=DiagnosticEvidenceAdmission(); e=a.admit_reproduced(a.admit_observed(base()), ReplayResult(True,()))
    with pytest.raises(ValueError): a.admit_verified(e, ReplayResult(False,("mismatch",)), EvaluationResult("PASS",(),e.evidence_digest))
