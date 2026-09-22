"""Verification scope bound to exact rule content identity."""
from __future__ import annotations
from dataclasses import dataclass
from gnosis.core.types import Candidate, TestResult, _stable_hash
from gnosis.core.rule_identity import RuleIdentity, verify_rule_identity

@dataclass(frozen=True)
class VerificationScope:
    rule_id: str
    rule_digest: str
    candidate_id: str
    scope: str

def verification_scope_digest(scope: VerificationScope) -> str:
    return _stable_hash({"rule_id":scope.rule_id,"rule_digest":scope.rule_digest,"candidate_id":scope.candidate_id,"scope":scope.scope})

def verify_result_scope(candidate: Candidate, result: TestResult, rule: RuleIdentity, scope: str, expected_digest: str, rule_content: object) -> None:
    if not verify_rule_identity(rule,rule_content):
        raise ValueError("rule identity mismatch")
    actual=verification_scope_digest(VerificationScope(rule.rule_id,rule.rule_digest,candidate.candidate_id,scope))
    if actual != expected_digest:
        raise ValueError("verification scope digest mismatch")
    if not result.passed:
        raise ValueError("verification scope result is not passing")
