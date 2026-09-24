import pytest

from gnosis.self_learning.collaboration_evidence import record_execution_evidence
from gnosis.self_learning.execution_recovery import reconcile_after_restart


def make(status="UNKNOWN"):
    return record_execution_evidence(
        authorization_id="a", authorization_digest="sha256:a",
        review_id="r", review_digest="sha256:r", proposal_id="p", proposal_revision="1",
        action_class="CREATE_PUBLIC_ISSUE_OR_PR", target_resource="repo:x",
        authorized_scope="issue:create", executor_id="e", execution_attempt_id="attempt-1",
        execution_order="1", result_status=status, privacy_classification="PUBLIC_APPROVED",
        observed_scope="issue:create", expected_preconditions=("current",), provenance_refs=("a","r","p"),
        result_evidence_sufficient=True,
    )


def test_restart_preserves_unknown():
    d = reconcile_after_restart(make("UNKNOWN"))
    assert d.disposition == "PRESERVE"
    assert d.prior_status == "UNKNOWN"


@pytest.mark.parametrize("status", ["FAILED", "PARTIAL", "UNKNOWN"])
def test_restart_never_inflates_non_success(status):
    d = reconcile_after_restart(make(status), new_result_status="SUCCEEDED", new_evidence_present=False)
    assert d.disposition == "REJECT_RETRY"
    assert d.prior_status == status


def test_new_evidence_can_reconcile_only_under_new_authorized_attempt():
    d = reconcile_after_restart(
        make("UNKNOWN"), new_result_status="SUCCEEDED",
        new_target_after_revision="r2", new_evidence_present=True, retry_authorized=True,
        new_attempt_id="attempt-2",
    )
    assert d.disposition == "RECONCILE_WITH_NEW_EVIDENCE"
    assert d.attempt_id == "attempt-2"


def test_recovery_cannot_authorize_retry():
    d = reconcile_after_restart(
        make("UNKNOWN"), new_result_status="SUCCEEDED", new_evidence_present=True,
        retry_authorized=False,
    )
    assert d.disposition == "REJECT_RETRY"


def test_retry_without_distinct_attempt_is_rejected():
    d = reconcile_after_restart(
        make("UNKNOWN"), new_result_status="SUCCEEDED",
        new_evidence_present=True, retry_authorized=True,
        new_attempt_id="attempt-1",
    )
    assert d.disposition == "REJECT_RETRY"


def test_recovery_does_not_execute_or_mutate_prior_evidence():
    prior = make("UNKNOWN")
    d = reconcile_after_restart(prior, new_result_status="SUCCEEDED", new_evidence_present=True, retry_authorized=False)
    assert d.disposition == "REJECT_RETRY"
    assert prior.result_status == "UNKNOWN"
