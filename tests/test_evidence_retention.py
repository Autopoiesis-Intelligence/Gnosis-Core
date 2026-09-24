import pytest
from gnosis.self_learning.evidence_retention import create_retention_decision,may_dispose,preserves_audit_reference
def make(policy="RETAIN",status="PROPOSED",basis="audit"):
    return create_retention_decision(contract_id="E7.83",evidence_refs=("evidence:1",),policy=policy,retention_basis=basis,disposal_scope="raw-private-data",privacy_classification="PRIVATE",status=status)
def test_retain_preserves_reference(): assert preserves_audit_reference(decision=make())
def test_disposal_is_gated(): assert not may_dispose(decision=make("DISPOSE","PROPOSED","MINIMIZE"))
def test_executed_disposal_requires_minimization():
    with pytest.raises(ValueError): make("DISPOSE","EXECUTED","audit")
def test_executed_disposal_with_minimization(): assert may_dispose(decision=make("DISPOSE","EXECUTED","MINIMIZE: privacy"))
def test_deterministic(): assert make()==make()