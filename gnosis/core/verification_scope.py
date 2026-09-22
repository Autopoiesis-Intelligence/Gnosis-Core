"""Verification-scope identity: bind a test result to rule and candidate scope."""
from __future__ import annotations
from dataclasses import dataclass
from gnosis.core.types import Candidate, TestResult, _stable_hash

@dataclass(frozen=True)
class VerificationScope:
    rule_id: str
    candidate_id: str
    scope: str

def verification_scope_digest(scope: VerificationScope) -> str:
    return _stable_hash({"rule_id":scope.rule_id,"candidate_id":scope.candidate_id,"scope":scope.scope})

def verify_result_scope(candidate: Candidate, result: TestResult, rule_id: str, scope: str, expected_digest: str) -> None:
    actual=verification_scope_digest(VerificationScope(rule_id,candidate.candidate_id,scope))
    if actual != expected_digest:
        raise ValueError("verification scope digest mismatch")
    if not result.passed:
        raise ValueError("verification scope result is not passing")
