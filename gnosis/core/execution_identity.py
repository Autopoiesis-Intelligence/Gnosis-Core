"""Canonical identity and provenance for a concrete verification execution."""
from __future__ import annotations
from dataclasses import dataclass
from gnosis.core.types import TestResult, _stable_hash
from gnosis.core.check_identity import CheckIdentity, verify_check_identity

@dataclass(frozen=True)
class ExecutionIdentity:
    check_digest: str
    input_digest: str
    context_digest: str
    result_digest: str

def execution_identity(check: CheckIdentity, input_value: object, context: object, result: TestResult) -> ExecutionIdentity:
    return ExecutionIdentity(
        check.check_digest,
        _stable_hash(input_value),
        _stable_hash(context),
        _stable_hash({"passed":result.passed,"reasons":tuple(result.reasons)}),
    )

def verify_execution_identity(identity: ExecutionIdentity, check: CheckIdentity, input_value: object, context: object, result: TestResult) -> bool:
    return identity == execution_identity(check,input_value,context,result)
