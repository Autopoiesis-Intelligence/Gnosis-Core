import pytest

from gnosis.self_learning.collaboration_authorization import (
    PreconditionEvidence,
    issue_execution_authorization,
    revoke_execution_authorization,
    validate_execution_request,
)


def target_revision_resolver(resource):
    return "target-r1"


def evidence_resolver(digest):
    return _EVIDENCE_BY_DIGEST.get(digest)


_EVIDENCE_BY_DIGEST = {}


def auth_precondition_evidence(auth):
    return PreconditionEvidence(source_id="trusted-review-engine", target_revision=auth.authorized_target_revision, evidence_revision="evidence-r1", observed_conditions=auth.preconditions, provenance="evidence-chain:r1")


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
        authorized_target_revision="target-r1",
    )
    base.update(overrides)
    base["precondition_evidence"] = PreconditionEvidence(
        source_id="trusted-review-engine",
        target_revision=base["authorized_target_revision"],
        evidence_revision="evidence-r1",
        observed_conditions=base["preconditions"],
        provenance="evidence-chain:r1",
    )
    return base


def test_exact_accepted_review_can_issue_authorization():
    auth = issue_execution_authorization(**_kwargs())
    assert auth.decision == "ALLOW"
    assert auth.authority == "execution-authorization-only"
    _EVIDENCE_BY_DIGEST[auth.precondition_evidence_digest] = auth_precondition_evidence(auth)
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
        target_revision_resolver=target_revision_resolver,
        evidence_resolver=evidence_resolver,
        now="2026-01-01T00:00:00Z",
    )


@pytest.mark.parametrize(
    "overrides",
    [
        {"review_decision": "REJECTED"},
        {"review_proposal_revision": "r0"},
        {"proposal_revision": "r2"},
        {"action_class": "UNSUPPORTED_ACTION"},
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
        target_revision_resolver=target_revision_resolver,
        evidence_resolver=evidence_resolver,
        now="2026-01-01T00:00:00Z",
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
        target_revision_resolver=lambda resource: "target-r2",
        evidence_resolver=evidence_resolver,
        now="2026-01-01T00:00:00Z",
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
        target_revision_resolver=target_revision_resolver,
        evidence_resolver=evidence_resolver,
        now="2026-01-01T00:00:00Z",
    )


def test_tampered_authorization_record_is_rejected():
    auth = issue_execution_authorization(**_kwargs())
    with pytest.raises(ValueError):
        type(auth)(
            **{**auth.__dict__, "authorized_scope": "issue:update"}
        )


def test_expired_authorization_is_denied():
    auth = issue_execution_authorization(**_kwargs(expires_at="2026-01-01T00:00:00Z"))
    assert not validate_execution_request(
        authorization=auth,
        review_id="review-1", review_digest="sha256:review",
        proposal_id="proposal-1", proposal_revision="r1",
        action_class="CREATE_PUBLIC_ISSUE_OR_PR",
        target_resource="repo:public/project", requested_scope="issue:create",
        executor_id="executor-1", privacy_classification="PUBLIC_APPROVED",
        current_target_revision="target-r1",
        current_precondition_evidence=auth_precondition_evidence(auth),
        now="2026-01-01T00:00:00Z",
    )


def test_caller_cannot_supply_authorized_target_revision():
    auth = issue_execution_authorization(**_kwargs())
    assert not validate_execution_request(
        authorization=auth,
        review_id="review-1", review_digest="sha256:review",
        proposal_id="proposal-1", proposal_revision="r1",
        action_class="CREATE_PUBLIC_ISSUE_OR_PR",
        target_resource="repo:public/project", requested_scope="issue:create",
        executor_id="executor-1", privacy_classification="PUBLIC_APPROVED",
        current_target_revision="target-r2",
        current_precondition_evidence=auth_precondition_evidence(auth),
        now="2026-01-01T00:00:00Z",
    )


def test_unsatisfied_precondition_evidence_is_denied():
    auth = issue_execution_authorization(**_kwargs())
    assert not validate_execution_request(
        authorization=auth,
        review_id="review-1", review_digest="sha256:review",
        proposal_id="proposal-1", proposal_revision="r1",
        action_class="CREATE_PUBLIC_ISSUE_OR_PR",
        target_resource="repo:public/project", requested_scope="issue:create",
        executor_id="executor-1", privacy_classification="PUBLIC_APPROVED",
        target_revision_resolver=target_revision_resolver,
        evidence_resolver=lambda digest: PreconditionEvidence(source_id="trusted-review-engine", target_revision="target-r1", evidence_revision="evidence-r2", observed_conditions=("review-current",), provenance="evidence-chain:r2"),
        now="2026-01-01T00:00:00Z",
    )


def test_canonical_identity_binds_target_and_precondition_evidence():
    auth = issue_execution_authorization(**_kwargs())
    with pytest.raises(ValueError):
        type(auth)(
            **{**auth.__dict__, "authorized_target_revision": "target-r2"}
        )
    with pytest.raises(ValueError):
        type(auth)(
            **{**auth.__dict__, "precondition_evidence_digest": "sha256:wrong"}
        )


def test_forged_precondition_digest_cannot_authorize():
    evidence = PreconditionEvidence(
        source_id="attacker",
        target_revision="target-r1",
        evidence_revision="fake",
        observed_conditions=("review-current", "target-current"),
        provenance="forged",
    )
    with pytest.raises(ValueError):
        issue_execution_authorization(**_kwargs(precondition_evidence=evidence))


def test_stale_precondition_evidence_is_denied():
    auth = issue_execution_authorization(**_kwargs())
    stale = PreconditionEvidence(
        source_id="trusted-review-engine",
        target_revision="target-r1",
        evidence_revision="evidence-r0",
        observed_conditions=auth.preconditions,
        provenance="evidence-chain:r0",
    )
    assert not validate_execution_request(
        authorization=auth,
        review_id="review-1", review_digest="sha256:review",
        proposal_id="proposal-1", proposal_revision="r1",
        action_class="CREATE_PUBLIC_ISSUE_OR_PR",
        target_resource="repo:public/project", requested_scope="issue:create",
        executor_id="executor-1", privacy_classification="PUBLIC_APPROVED",
        target_revision_resolver=target_revision_resolver,
        evidence_resolver=lambda digest: stale,
        now="2026-01-01T00:00:00Z",
    )


@pytest.mark.parametrize("bad_timestamp", ["2099-01-01T00:00:00+00:00", "2099-01-01T00:00:00", "not-a-timestamp"])
def test_noncanonical_expiry_timestamp_is_rejected(bad_timestamp):
    with pytest.raises(ValueError):
        issue_execution_authorization(**_kwargs(expires_at=bad_timestamp))


def test_malformed_execution_time_is_denied():
    auth = issue_execution_authorization(**_kwargs())
    assert not validate_execution_request(
        authorization=auth,
        review_id="review-1", review_digest="sha256:review",
        proposal_id="proposal-1", proposal_revision="r1",
        action_class="CREATE_PUBLIC_ISSUE_OR_PR",
        target_resource="repo:public/project", requested_scope="issue:create",
        executor_id="executor-1", privacy_classification="PUBLIC_APPROVED",
        current_target_revision="target-r1",
        current_precondition_evidence=auth_precondition_evidence(auth),
        now="not-a-timestamp",
    )
