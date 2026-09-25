import pytest

from gnosis.self_learning.canonical_commit_guard import validate_before_canonical_commit


@pytest.mark.parametrize(
    "kwargs, message",
    [
        (
            dict(
                parent_state_digest="sha256:same",
                candidate_state_digest="sha256:same",
                evidence_verified=True,
                replay_detected=False,
            ),
            "no-op",
        ),
        (
            dict(
                parent_state_digest="sha256:old",
                candidate_state_digest="sha256:new",
                evidence_verified=False,
                replay_detected=False,
            ),
            "unverified",
        ),
        (
            dict(
                parent_state_digest="sha256:old",
                candidate_state_digest="sha256:new",
                evidence_verified=True,
                replay_detected=True,
            ),
            "replayed",
        ),
    ],
)
def test_invalid_learning_cannot_cross_canonical_commit_boundary(kwargs, message):
    with pytest.raises(ValueError, match=message):
        validate_before_canonical_commit(**kwargs)


def test_valid_learning_crosses_guard():
    validate_before_canonical_commit(
        parent_state_digest="sha256:old",
        candidate_state_digest="sha256:new",
        evidence_verified=True,
        replay_detected=False,
    )
