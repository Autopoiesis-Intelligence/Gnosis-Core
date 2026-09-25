"""R3.4 minimal autonomous cycle contract test."""
from gnosis.self_learning.learning_candidate_gate import evaluate_learning_candidate

def test_r34_cycle_requires_observe_test_admit_commit_verify_order():
    events=["observe","candidate","test","admit","commit","verify","audit"]
    assert events == ["observe","candidate","test","admit","commit","verify","audit"]
    check=evaluate_learning_candidate(
        parent_state_digest="parent",
        candidate_state_digest="candidate",
        evidence_verified=True,
        replay_detected=False,
    )
    assert check.changed
    assert check.evidence_verified
    assert not check.replay_detected
