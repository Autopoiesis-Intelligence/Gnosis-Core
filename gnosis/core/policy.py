"""Authoritative executable-policy binding for trusted Core evaluation.

The binding couples policy identity to the exact callable used for evaluation.
Raw callables remain available only through the legacy/untrusted Engine path.
"""
from __future__ import annotations

import hashlib
import inspect
from dataclasses import dataclass, field
from typing import Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from .types import Candidate, State, TestResult

PolicyCallable = Callable[["State", "Candidate"], bool]

class _RegistryAuthorityToken:
    __slots__ = ()

_REGISTRY_AUTHORITY = _RegistryAuthorityToken()


class _PolicyAuthorityToken:
    __slots__ = ()

_AUTHORITY = _PolicyAuthorityToken()


def implementation_identity(evaluator: PolicyCallable) -> str:
    """Return a deterministic identity for a registered Python evaluator."""
    module = getattr(evaluator, "__module__", "")
    qualname = getattr(evaluator, "__qualname__", getattr(evaluator, "__name__", ""))
    try:
        source = inspect.getsource(evaluator)
    except (OSError, TypeError):
        source = ""
    payload = f"{module}\n{qualname}\n{source}"
    return "python-source-sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class PolicyIdentity:
    rule_id: str
    rule_version: int
    implementation_identity: str

    def __post_init__(self) -> None:
        if not self.rule_id or self.rule_version < 1 or not self.implementation_identity:
            raise ValueError("complete policy identity is required")

    @property
    def key(self) -> tuple[str, int]:
        return self.rule_id, self.rule_version


@dataclass(frozen=True)
class EvaluationEvidence:
    policy: PolicyIdentity
    passed: bool
    invoked: bool
    candidate_id: str
    parent_state_id: str

    def __post_init__(self) -> None:
        if not isinstance(self.passed, bool) or not isinstance(self.invoked, bool):
            raise TypeError("evaluation evidence flags must be bool")
        if self.invoked is False and self.passed:
            raise ValueError("non-invoked evaluation cannot pass")


@dataclass(frozen=True)
class ExecutablePolicyBinding:
    """One immutable policy identity paired with its runtime evaluator."""
    policy: PolicyIdentity
    evaluator: PolicyCallable
    _authority: object = field(default=None, repr=False)

    def __post_init__(self) -> None:
        if self._authority is not _AUTHORITY:
            raise PermissionError("executable policy binding requires trusted authority")
        if implementation_identity(self.evaluator) != self.policy.implementation_identity:
            raise ValueError("evaluator does not match policy implementation identity")

    def evaluate(self, current: "State", candidate: "Candidate") -> tuple["TestResult", EvaluationEvidence]:
        from .types import TestResult

        passed = self.evaluator(current, candidate)
        if not isinstance(passed, bool):
            raise TypeError("registered policy evaluator must return bool")
        result = TestResult(
            passed=passed,
            reasons=(
                "registered policy passed",
            ) if passed else (
                "registered policy rejected candidate",
            ),
        )
        return result, EvaluationEvidence(
            policy=self.policy,
            passed=passed,
            invoked=True,
            candidate_id=candidate.candidate_id,
            parent_state_id=current.state_id,
        )


def default_policy_binding() -> ExecutablePolicyBinding:
    from .verification import default_test
    return _issue_binding("test-rule:default", 1, default_test)


def _issue_binding(rule_id: str, rule_version: int, evaluator: PolicyCallable) -> ExecutablePolicyBinding:
    return ExecutablePolicyBinding(
        policy=PolicyIdentity(rule_id, rule_version, implementation_identity(evaluator)),
        evaluator=evaluator,
    )


def bind_policy(rule_id: str, rule_version: int, evaluator: PolicyCallable) -> ExecutablePolicyBinding:
    """Compatibility helper for tests/legacy code; not registry-authorized."""
    raise PermissionError("use RuleRegistry.resolve() for trusted executable policy binding")
