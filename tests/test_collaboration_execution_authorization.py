import pytest
from gnosis.self_learning.collaboration_execution_authorization import issue_authorization,authorization_valid

def make():
    return issue_authorization(review_id="sha256:review",proposal_id="sha256:proposal",proposal_revision="r1",review_decision="ACCEPTED",action="PUBLISH_PUBLIC",target_resource="github:repo",authorized_scope="public:proposal",executor_id="executor",authorization_basis="review:accepted",privacy_classification="SHAREABLE_ABSTRACTION",issuance_revision="auth:r1",expiry_evidence="expiry:e1",revocation_state="ACTIVE",preconditions=("privacy:pass",))

def test_authorization_is_valid_only_for_exact_tuple():
    a=make()
    assert authorization_valid(authorization=a,review_id="sha256:review",proposal_revision="r1",action="PUBLISH_PUBLIC",target_resource="github:repo",scope="public:proposal",privacy_classification="SHAREABLE_ABSTRACTION")
    assert not authorization_valid(authorization=a,review_id="sha256:review",proposal_revision="r2",action="PUBLISH_PUBLIC",target_resource="github:repo",scope="public:proposal",privacy_classification="SHAREABLE_ABSTRACTION")

@pytest.mark.parametrize("decision",["REJECTED","DEFERRED","RETURNED_FOR_REVISION"])
def test_nonaccepted_review_cannot_issue(decision):
    with pytest.raises(ValueError): issue_authorization(review_id="r",proposal_id="p",proposal_revision="r1",review_decision=decision,action="PUBLISH_PUBLIC",target_resource="github:repo",authorized_scope="public",executor_id="e",authorization_basis="b",privacy_classification="SHAREABLE_ABSTRACTION",issuance_revision="a",expiry_evidence="x",revocation_state="ACTIVE",preconditions=("p",))

def test_revoked_expired_stale_fail_closed():
    a=make()
    for kwargs in ({"revoked":True},{"expired":True},{"stale":True}):
        assert not authorization_valid(authorization=a,review_id="sha256:review",proposal_revision="r1",action="PUBLISH_PUBLIC",target_resource="github:repo",scope="public:proposal",privacy_classification="SHAREABLE_ABSTRACTION",**kwargs)

def test_unknown_action_rejected():
    with pytest.raises(ValueError):
        issue_authorization(review_id="r",proposal_id="p",proposal_revision="r1",review_decision="ACCEPTED",action="DELETE_ALL",target_resource="x",authorized_scope="x",executor_id="e",authorization_basis="b",privacy_classification="SHAREABLE_ABSTRACTION",issuance_revision="a",expiry_evidence="x",revocation_state="ACTIVE",preconditions=("p",))

def test_identity_is_deterministic():
    assert make()==make()
