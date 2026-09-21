"""Canonical in-Core diagnostic corpus contract.

This is deliberately distinct from the external Research Machine corpus.
Cases are bounded diagnostic scenarios executed against Core state through the
existing sandbox/evidence boundary. They never receive authority to mutate
canonical state.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping

from gnosis.core.types import Candidate, State
from .sandbox import SandboxBudget, SandboxResult, run_sandbox

DiagnosticObservation = Callable[[State, Candidate], Mapping[str, object]]


@dataclass(frozen=True)
class CoreDiagnosticCase:
    case_id: str
    description: str
    observe: DiagnosticObservation
    budget: SandboxBudget = SandboxBudget()

    def __post_init__(self) -> None:
        if not self.case_id.strip():
            raise ValueError("diagnostic case_id must be non-empty")


@dataclass(frozen=True)
class CoreDiagnosticCorpus:
    """Immutable registry of bounded diagnostic cases owned by Core."""

    cases: tuple[CoreDiagnosticCase, ...] = ()

    def __post_init__(self) -> None:
        ids = [case.case_id for case in self.cases]
        if len(ids) != len(set(ids)):
            raise ValueError("diagnostic case_id values must be unique")

    def case(self, case_id: str) -> CoreDiagnosticCase:
        for case in self.cases:
            if case.case_id == case_id:
                return case
        raise KeyError(case_id)

    def run(self, case_id: str, state: State, candidate: Candidate) -> SandboxResult:
        case = self.case(case_id)
        return run_sandbox(state, candidate, case.observe, budget=case.budget)
