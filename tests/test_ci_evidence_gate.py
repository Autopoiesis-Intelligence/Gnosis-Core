import pytest

from gnosis.self_learning.ci_evidence_gate import (
    create_ci_evidence,
    may_admit_learning,
    may_prove_ci,
)

def make(**overrides):
    values = dict(
        commit_sha="abc123",
        workflow_run_id="100",
        job_id="200",
        scope="e7.60",
        execution_observed=True,
        result="PASS",
        evidence_digest="sha256:evidence",
        status="OBSERVED",
    )
    values.update(overrides)
    return create_ci_evidence(**values)

def test_valid_executed_ci_can_prove_and_admit():
    evidence = make()
    assert may_prove_ci(evidence=evidence, expected_commit_sha="abc123", expected_scope="e7.60")
    assert may_admit_learning(evidence=evidence, expected_commit_sha="abc123", expected_scope="e7.60")

@pytest.mark.parametrize(
    "overrides",
    [
        {"commit_sha": "other"},
        {"scope": "different"},
    ],
)
def test_sha_or_scope_substitution_is_rejected(overrides):
    evidence = make(**overrides)
    assert not may_prove_ci(evidence=evidence, expected_commit_sha="abc123", expected_scope="e7.60")

def test_job_without_observed_execution_cannot_be_proven():
    evidence = make(execution_observed=False, status="UNVERIFIED")
    assert not may_prove_ci(evidence=evidence, expected_commit_sha="abc123", expected_scope="e7.60")
    assert not may_admit_learning(evidence=evidence, expected_commit_sha="abc123", expected_scope="e7.60")

def test_observed_failed_ci_is_not_learning_admission():
    evidence = make(result="FAIL")
    assert may_prove_ci(evidence=evidence, expected_commit_sha="abc123", expected_scope="e7.60")
    assert not may_admit_learning(evidence=evidence, expected_commit_sha="abc123", expected_scope="e7.60")

def test_ci_evidence_never_creates_execution_authority():
    from gnosis.self_learning.ci_evidence_gate import creates_execution_authority
    assert creates_execution_authority(evidence=make()) is False
