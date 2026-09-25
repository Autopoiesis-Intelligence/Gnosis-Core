import pytest

from gnosis.self_learning.canonical_commit_guard import validate_before_canonical_commit


def test_guard_rejects_noop_before_commit():
    with pytest.raises(ValueError, match="no-op"):
        validate_before_canonical_commit(
            parent_state_digest="sha256:same",
            candidate_state_digest="sha256:same",
            evidence_verified=True,
            replay_detected=False,
        )
