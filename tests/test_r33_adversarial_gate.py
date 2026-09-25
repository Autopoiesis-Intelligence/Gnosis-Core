import pytest
from gnosis.self_learning.learning_candidate_gate import evaluate_learning_candidate

@pytest.mark.parametrize("kwargs",[
    dict(parent_state_digest="p",candidate_state_digest="p",evidence_verified=True,replay_detected=False),
    dict(parent_state_digest="p",candidate_state_digest="c",evidence_verified=False,replay_detected=False),
    dict(parent_state_digest="p",candidate_state_digest="c",evidence_verified=True,replay_detected=True),
])
def test_r33_adversarial_candidates_rejected(kwargs):
    with pytest.raises(ValueError):
        evaluate_learning_candidate(**kwargs)

def test_r33_valid_changed_verified_candidate_allowed():
    assert evaluate_learning_candidate(
        parent_state_digest="p",candidate_state_digest="c",
        evidence_verified=True,replay_detected=False
    ).changed
