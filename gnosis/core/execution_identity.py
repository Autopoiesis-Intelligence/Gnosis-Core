"""Canonical identity and provenance for a concrete verification execution."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json

from gnosis.core.check_identity import CheckIdentity
from gnosis.core.execution_input import ExecutionInput
from gnosis.core.types import TestResult, _stable_hash


@dataclass(frozen=True)
class ExecutionIdentity:
    check_digest: str
    input_digest: str
    context_digest: str
    result_digest: str


def execution_identity(
    check: CheckIdentity,
    input_value: object,
    context: object,
    result: TestResult,
) -> ExecutionIdentity:
    return ExecutionIdentity(
        check.check_digest,
        _stable_hash(input_value),
        _stable_hash(context),
        _stable_hash({"passed": result.passed, "reasons": tuple(result.reasons)}),
    )


def execution_identity_from_input(
    check: CheckIdentity,
    execution_input: ExecutionInput,
    context: object,
    result: TestResult,
) -> ExecutionIdentity:
    """Create identity from the canonical ExecutionInput contract.

    The input digest is never supplied independently; it is derived from the
    immutable canonical ExecutionInput representation.
    """
    base = execution_identity(check, execution_input, context, result)
    return ExecutionIdentity(
        check_digest=base.check_digest,
        input_digest=execution_input.digest,
        context_digest=base.context_digest,
        result_digest=base.result_digest,
    )


def verify_execution_identity(
    identity: ExecutionIdentity,
    check: CheckIdentity,
    input_value: object,
    context: object,
    result: TestResult,
) -> bool:
    return identity == execution_identity(check, input_value, context, result)


def verify_execution_identity_from_input(
    identity: ExecutionIdentity,
    check: CheckIdentity,
    execution_input: ExecutionInput,
    context: object,
    result: TestResult,
) -> bool:
    return identity == execution_identity_from_input(
        check, execution_input, context, result
    )
