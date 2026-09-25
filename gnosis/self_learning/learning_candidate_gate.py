"""R3.3 false-learning and no-op admission gate."""
from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class LearningCandidateCheck:
    parent_state_digest: str
    candidate_state_digest: str
    evidence_verified: bool
    replay_detected: bool
    changed: bool


def evaluate_learning_candidate(
    *,
    parent_state_digest: str,
    candidate_state_digest: str,
    evidence_verified: bool,
    replay_detected: bool,
) -> LearningCandidateCheck:
    changed = parent_state_digest != candidate_state_digest
    if replay_detected:
        raise ValueError("replayed evidence cannot authorize learning")
    if not evidence_verified:
        raise ValueError("unverified evidence cannot authorize learning")
    if not changed:
        raise ValueError("no-op candidate cannot authorize learning")
    return LearningCandidateCheck(
        parent_state_digest=parent_state_digest,
        candidate_state_digest=candidate_state_digest,
        evidence_verified=evidence_verified,
        replay_detected=replay_detected,
        changed=changed,
    )
