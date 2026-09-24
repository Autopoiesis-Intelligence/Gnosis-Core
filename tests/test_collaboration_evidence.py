import pytest

from gnosis.self_learning.collaboration_evidence import (
    record_execution_evidence,
    validate_observation_against_authorization,
)


def _kwargs(**overrides):
    base = dict(
        authorization_id="auth-1", authorization_digest="sha256:auth",
        review_id="review-1", review_digest="sha256:review",
        proposal_id="proposal-1", proposal_revision="r1",
        action_class="CREATE_PUBLIC_ISSUE_OR_PR", target_resource="repo:public/project",
        authorized_scope="issue:create", executor_id="executor-1",
        execution_attempt_id="attempt-1", execution_order="order-1",
        result_status="SUCCEEDED", target_before_revision="target-r1",
        target_after_revision="target-r2", privacy_classification="PUBLIC_APPROVED",
        observed_scope="issue:create", expected_preconditions=("target-current",),
        provenance_refs=("auth-1", "review-1", "proposal-1"),
    )
    base.update(overrides)
    return base


def test_success_is_reconciled_only_when_binding_matches():
    evidence = record_execution_evidence(**_kwargs())
    assert evidence.reconciliation_status == "RECONCILED"
    assert validate_observation_against_authorization(
        evidence=evidence, authorization_id="auth-1", authorization_digest="sha256:auth",
        review_id="review-1", review_digest="sha256:review", proposal_id="proposal-1",
        proposal_revision="r1", action_class="CREATE_PUBLIC_ISSUE_OR_PR",
        target_resource="repo:public/project", authorized_scope="issue:create",
        observed_scope="issue:create", execution_attempt_id="attempt-1",
        result_status="SUCCEEDED",
    )


@pytest.mark.parametrize("result_status", ["UNKNOWN", "PARTIAL", "FAILED", "NOT_ATTEMPTED", "REJECTED_BY_BOUNDARY"])
def test_non_success_never_becomes_reconciled(result_status):
    evidence = record_execution_evidence(**_kwargs(result_status=result_status))
    assert evidence.reconciliation_status != "RECONCILED"


@pytest.mark.parametrize("flag", [
    "authorization_valid", "linkage_valid", "target_matches", "scope_matches",
    "result_evidence_sufficient", "privacy_matches", "before_after_consistent",
])
def test_boundary_conflict_fails_closed(flag):
    evidence = record_execution_evidence(**_kwargs(**{flag: False}))
    assert evidence.reconciliation_status == "REJECTED"


def test_conflicting_duplicate_fails_closed():
    with pytest.raises(ValueError):
        record_execution_evidence(**_kwargs(duplicate_conflict=True))


def test_scope_mismatch_cannot_validate():
    evidence = record_execution_evidence(**_kwargs(observed_scope="issue:update"))
    assert evidence.reconciliation_status == "REJECTED"
    assert not validate_observation_against_authorization(
        evidence=evidence, authorization_id="auth-1", authorization_digest="sha256:auth",
        review_id="review-1", review_digest="sha256:review", proposal_id="proposal-1",
        proposal_revision="r1", action_class="CREATE_PUBLIC_ISSUE_OR_PR",
        target_resource="repo:public/project", authorized_scope="issue:create",
        observed_scope="issue:update", execution_attempt_id="attempt-1",
        result_status="SUCCEEDED",
    )


def test_tampered_evidence_digest_is_rejected():
    evidence = record_execution_evidence(**_kwargs())
    with pytest.raises(ValueError):
        type(evidence)(**{**evidence.__dict__, "observed_scope": "issue:update"})


def test_duplicate_exact_observation_can_have_same_identity():
    first = record_execution_evidence(**_kwargs())
    second = record_execution_evidence(**_kwargs())
    assert first.evidence_id == second.evidence_id
    assert first.evidence_digest == second.evidence_digest
