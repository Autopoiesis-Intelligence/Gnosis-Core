import pytest
from gnosis.self_learning.collaboration_execution_evidence import create_execution_evidence,reconciled

def make(result="SUCCEEDED",recon="RECONCILED"):
    return create_execution_evidence(authorization_id="sha256:auth",review_id="sha256:review",proposal_revision="r1",action="PUBLISH_PUBLIC",target_resource="github:repo",authorized_scope="public:proposal",executor_id="executor",attempt_id="attempt:1",ordering_evidence="order:1",result_status=result,target_before="sha256:before",target_after="sha256:after",privacy_classification="SHAREABLE_ABSTRACTION",reconciliation_status=recon,provenance_refs=("auth:1","attempt:1"))

def test_success_requires_reconciled():
    assert reconciled(evidence=make(),authorization_id="sha256:auth",action="PUBLISH_PUBLIC",target_resource="github:repo",scope="public:proposal",privacy_classification="SHAREABLE_ABSTRACTION")

@pytest.mark.parametrize("result",["UNKNOWN","FAILED","PARTIAL","REJECTED_BY_BOUNDARY"])
def test_non_success_cannot_be_reconciled(result):
    with pytest.raises(ValueError): make(result,"RECONCILED")

def test_mismatch_is_not_success():
    assert not reconciled(evidence=make("SUCCEEDED","MISMATCH"),authorization_id="sha256:auth",action="PUBLISH_PUBLIC",target_resource="github:repo",scope="public:proposal",privacy_classification="SHAREABLE_ABSTRACTION")

def test_conflicting_tuple_is_not_reconciled():
    assert not reconciled(evidence=make(),authorization_id="sha256:other",action="PUBLISH_PUBLIC",target_resource="github:repo",scope="public:proposal",privacy_classification="SHAREABLE_ABSTRACTION")

def test_identity_is_deterministic():
    assert make()==make()
