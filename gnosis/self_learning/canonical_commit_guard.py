"""R3.3 canonical commit-boundary guard.

The guard is deliberately pure: it does not persist or mutate state.
"""
from __future__ import annotations

from gnosis.self_learning.learning_candidate_gate import evaluate_learning_candidate


def validate_before_canonical_commit(
    *,
    parent_state_digest: str,
    candidate_state_digest: str,
    evidence_verified: bool,
    replay_detected: bool,
) -> None:
    evaluate_learning_candidate(
        parent_state_digest=parent_state_digest,
        candidate_state_digest=candidate_state_digest,
        evidence_verified=evidence_verified,
        replay_detected=replay_detected,
    )
