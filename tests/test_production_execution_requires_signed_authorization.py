"""Security regression tests for the signed owner-authorization commit boundary."""
import pytest

from gnosis.reflection.execution_adapter import SQLiteExecutionCommitAdapter
from gnosis.reflection.trusted_execution_gate import require_trusted_execution


def test_commit_rejects_missing_signed_authorization_before_touching_storage():
    with pytest.raises(PermissionError, match="signed production owner authorization is required"):
        SQLiteExecutionCommitAdapter().commit(
            None, None, None, None, None, actor="test",
        )


@pytest.mark.parametrize(
    ("policy", "digest", "message"),
    [
        ("", "digest", "trusted expected policy version is required"),
        ("policy-v1", "", "trusted expected validity evidence digest is required"),
    ],
)
def test_gate_rejects_missing_independent_trust_anchors(policy, digest, message):
    with pytest.raises(PermissionError, match=message):
        require_trusted_execution(
            None, conn=None, actor="test",
            expected_policy_version=policy,
            expected_evidence_digest=digest,
        )
