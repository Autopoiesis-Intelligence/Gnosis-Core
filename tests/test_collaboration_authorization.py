import pytest

from gnosis.self_learning.collaboration_authorization import (
    issue_execution_authorization,
    revoke_execution_authorization,
    validate_execution_request,
)


def _kwargs(**overrides):
    base = dict(
        review_id="review-1",
        review_digest="sha256:review",
        review_decision="ACCEPTED",
        review_proposal_id="proposal-1",
        review_proposal_revision="r1",
        proposal_id="proposal-1",
        proposal_revision="r1",
        action_class="CREATE_PUBLIC_ISSUE_OR_PR",
        target_resource="repo:public/project",
        authorized_scope="issue:create",
        executor_id="executor-1",
        authorization_basis="owner-review",
        privacy_classification="PUBLIC_APPROVED",
        issuance_revision="auth-r1",
        expires_at="2099-01-01T00:00:00Z",
        preconditions=("review-current", "target-current"),
    )
    base.update(overrides)
    return base


def test_exact_accepted_review_can_issue_authorization():
    auth = issue_execution_authorization(**_kwargs())
    assert auth.decision == "ALLOW"
    assert auth.authority == "execution-authorization-only"
    assert validate_execution_request(
        authorization=auth,
        review_id="review-1",
        review_digest="sha256:review",
        proposal_id="proposal-1",
        proposal_revision="r1",
        action_class="CREATE_PUBLIC_ISSUE_OR_PR",
        target_resource="repo:public/project",
        requested_scope="issue:create",
        executor_id="executor-1",
        privacy_classification="PUBLIC_APPROVED",
        current_target_revision="target-r1",
        authorized_target_revision="target-r1",
    )


@pytest.mark.parametrize(
    "overrides",
    [
        {"review_decision": "REJECTED"},
        {"review_proposal_revision": "r0"},
        {"proposal_revision": "r2"},
        {"action_class": "SEND_INVITATION", "target_resource": "repo:other"},
        {"privacy_classification": "UNKNOWN"},
        {"stale": True},
        {"revoked": True},
        {"scope_allowed": False},
        {"provenance_complete": False},
        {"required_preconditions_present": False},
    ],
)
def test_fail_closed_issue_gate(overrides):
    with pytest.raises(ValueError):
        issue_execution_authorization(**_kwargs(**overrides))


def test_conflicting_request_is_denied():
    auth = issue_execution_authorization(**_kwargs())
    assert not validate_execution_request(
        authorization=auth,
        review_id="review-1",
        review_digest="sha256:review",
        proposal_id="proposal-1",
        proposal_revision="r1",
        action_class="CREATE_PUBLIC_ISSUE_OR_PR",
        target_resource="repo:public/project",
        requested_scope="issue:update",
        executor_id="executor-1",
        privacy_classification="PUBLIC_APPROVED",
        current_target_revision="target-r1",
        authorized_target_revision="target-r1",
    )


def test_target_advance_makes_authorization_stale():
    auth = issue_execution_authorization(**_kwargs())
    assert not validate_execution_request(
        authorization=auth,
        review_id="review-1",
        review_digest="sha256:review",
        proposal_id="proposal-1",
        proposal_revision="r1",
        action_class="CREATE_PUBLIC_ISSUE_OR_PR",
        target_resource="repo:public/project",
        requested_scope="issue:create",
        executor_id="executor-1",
        privacy_classification="PUBLIC_APPROVED",
        current_target_revision="target-r2",
        authorized_target_revision="target-r1",
    )


def test_revocation_changes_identity_and_denies_reuse():
    auth = issue_execution_authorization(**_kwargs())
    revoked = revoke_execution_authorization(auth, revocation_revision="revoke-1")
    assert revoked.authorization_id != auth.authorization_id
    assert revoked.decision == "DENY"
    assert not validate_execution_request(
        authorization=revoked,
        review_id="review-1",
        review_digest="sha256:review",
        proposal_id="proposal-1",
        proposal_revision="r1",
        action_class="CREATE_PUBLIC_ISSUE_OR_PR",
        target_resource="repo:public/project",
        requested_scope="issue:create",
        executor_id="executor-1",
        privacy_classification="PUBLIC_APPROVED",
        current_target_revision="target-r1",
        authorized_target_revision="target-r1",
    )


def test_tampered_authorization_record_is_rejected():
    auth = issue_execution_authorization(**_kwargs())
    with pytest.raises(ValueError):
        type(auth)(
            **{**auth.__dict__, "authorized_scope": "issue:update"}
        )
