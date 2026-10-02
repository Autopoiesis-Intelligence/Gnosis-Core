import pytest

from gnosis.self_learning.ci_evidence_gate import create_ci_evidence
from gnosis.self_learning.ci_learning_admission import admit_ci_evidence


def make(**overrides):
    values = dict(
        commit_sha="abc123",
        workflow_run_id="100",
        job_id="200",
        scope="first-task",
        execution_observed=True,
        result="PASS",
        evidence_digest="sha256:evidence",
        status="OBSERVED",
    )
    values.update(overrides)
    return create_ci_evidence(**values)


def test_proven_ci_evidence_becomes_admitted_learning_evidence():
    admission = admit_ci_evidence(
        evidence=make(),
        expected_commit_sha="abc123",
        expected_scope="first-task",
    )
    assert admission.status == "ADMITTED"
    assert admission.evidence_digest == "sha256:evidence"
    assert "workflow:100" in admission.verification_refs
    assert "job:200" in admission.verification_refs
    assert admission.source_contract_id.startswith("sha256:")


@pytest.mark.parametrize(
    "overrides",
    [
        {"execution_observed": False, "status": "UNVERIFIED"},
        {"commit_sha": "other"},
        {"scope": "other"},
        {"result": "FAIL"},
    ],
)
def test_unproven_ci_cannot_become_learning_admission(overrides):
    with pytest.raises(PermissionError, match="not proven"):
        admit_ci_evidence(
            evidence=make(**overrides),
            expected_commit_sha="abc123",
            expected_scope="first-task",
        )


def test_learning_adapter_creates_no_execution_authority():
    admission = admit_ci_evidence(
        evidence=make(),
        expected_commit_sha="abc123",
        expected_scope="first-task",
    )
    from gnosis.self_learning.ci_learning_admission import creates_execution_authority
    assert creates_execution_authority(admission=admission) is False
