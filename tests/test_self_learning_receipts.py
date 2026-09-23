import pytest
from gnosis.self_learning.execution import create_execution_plan
from gnosis.self_learning.governance import create_review
from gnosis.self_learning.proposals import propose_from_finding
from gnosis.self_learning.receipts import create_mutation_receipt, receipt_digest, validate_receipt_plan_binding
from gnosis.self_learning.validation import validate_proposal

def _plan(finding="STATUS_DRIFT:E7.01:registry=X:artifact=Y"):

    proposal=propose_from_finding(finding)
    validation=validate_proposal(proposal,known_contract_ids=["E7.01"],known_findings=[finding])
    review=create_review(proposal,validation,decision="ACCEPTED",reviewer="r",reason="ok",created_at="2026-09-23T12:00:00+00:00")
    return create_execution_plan(review)

def test_applied_receipt_is_deterministic_for_fixed_inputs():
    plan=_plan()
    args=dict(result="APPLIED",target="registry:E7.01",before_digest="sha256:a",after_digest="sha256:b",executor="executor-1",authorization_reference="auth-1",created_at="2026-09-23T12:00:00+00:00")
    assert create_mutation_receipt(plan,**args)==create_mutation_receipt(plan,**args)

def test_applied_requires_digest_change():
    with pytest.raises(ValueError,match="must change"):
        create_mutation_receipt(_plan(),result="APPLIED",target="x",before_digest="same",after_digest="same",executor="e",authorization_reference="a")

def test_receipt_is_evidence_only():
    r=create_mutation_receipt(_plan(),result="APPLIED",target="x",before_digest="a",after_digest="b",executor="e",authorization_reference="a",created_at="2026-09-23T12:00:00+00:00")
    assert r.authority=="evidence-only"

def test_receipt_digest_is_order_independent():
    plan=_plan()
    a=create_mutation_receipt(plan,result="REJECTED",target="x",before_digest="a",after_digest="a",executor="e",authorization_reference="a",created_at="2026-09-23T12:00:00+00:00")
    b=create_mutation_receipt(plan,result="FAILED",target="y",before_digest="b",after_digest="b",executor="e",authorization_reference="b",created_at="2026-09-23T12:00:01+00:00")
    assert receipt_digest([a,b])==receipt_digest([b,a])


def test_receipt_cannot_be_bound_to_a_different_plan():
    first=_plan("STATUS_DRIFT:E7.01:registry=X:artifact=Y")
    second=_plan("STATUS_DRIFT:E7.02:registry=X:artifact=Z")
    receipt=create_mutation_receipt(first,result="APPLIED",target="x",before_digest="a",after_digest="b",executor="e",authorization_reference="a",created_at="2026-09-23T12:00:00+00:00")
    with pytest.raises(PermissionError,match="plan identity mismatch"):
        validate_receipt_plan_binding(receipt,second)
