import pytest

from gnosis.self_learning.learning_candidate_gate import evaluate_learning_candidate


def test_noop_candidate_is_rejected():
    with pytest.raises(ValueError, match="no-op"):
        evaluate_learning_candidate(
            parent_state_digest="sha256:same",
            candidate_state_digest="sha256:same",
            evidence_verified=True,
            replay_detected=False,
        )


def test_unverified_evidence_is_rejected():
    with pytest.raises(ValueError, match="unverified"):
        evaluate_learning_candidate(
            parent_state_digest="sha256:old",
            candidate_state_digest="sha256:new",
            evidence_verified=False,
            replay_detected=False,
        )


def test_replayed_evidence_is_rejected():
    with pytest.raises(ValueError, match="replayed"):
        evaluate_learning_candidate(
            parent_state_digest="sha256:old",
            candidate_state_digest="sha256:new",
            evidence_verified=True,
            replay_detected=True,
        )


def test_verified_new_candidate_is_admissible():
    result = evaluate_learning_candidate(
        parent_state_digest="sha256:old",
        candidate_state_digest="sha256:new",
        evidence_verified=True,
        replay_detected=False,
    )
    assert result.changed
