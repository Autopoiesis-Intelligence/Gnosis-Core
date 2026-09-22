"""Canonical identity for TestResult and binding to evolution."""
from __future__ import annotations
from gnosis.core.types import TestResult, Candidate, TransitionRecord, _stable_hash

def test_result_digest(result: TestResult) -> str:
    return _stable_hash({"passed": result.passed, "reasons": tuple(result.reasons)})

def verify_test_transition_binding(candidate: Candidate, result: TestResult, transition: TransitionRecord, expected_digest: str) -> None:
    if transition.candidate_id != candidate.candidate_id:
        raise ValueError("transition candidate_id mismatch")
    if not result.passed and transition.accepted:
        raise ValueError("accepted transition has failing test result")
    if transition.test_result != result:
        raise ValueError("transition test result mismatch")
    if test_result_digest(result) != expected_digest:
        raise ValueError("test result digest mismatch")
