from gnosis.self_learning.e7_109_evidence_acceptance import EvidenceItem, AcceptanceState, accept_evidence

def item(passed=True, evidence="EV1", expected="pass", observed="pass"):
    return EvidenceItem("C1", evidence, expected, observed, passed)

def test_empty_evidence_blocks():
    assert accept_evidence(batch_id="B", execution_record_id="E", items=()).state is AcceptanceState.BLOCKED

def test_missing_identity_rejects():
    assert accept_evidence(batch_id="B", execution_record_id="E", items=(item(evidence=""),)).state is AcceptanceState.REJECTED

def test_incomplete_evidence_rejects():
    assert accept_evidence(batch_id="B", execution_record_id="E", items=(item(expected=""),)).state is AcceptanceState.REJECTED

def test_failed_criterion_rejects():
    assert accept_evidence(batch_id="B", execution_record_id="E", items=(item(False),)).state is AcceptanceState.REJECTED

def test_complete_passing_evidence_is_accepted():
    r=accept_evidence(batch_id="B", execution_record_id="E", items=(item(),))
    assert r.state is AcceptanceState.ACCEPTED
