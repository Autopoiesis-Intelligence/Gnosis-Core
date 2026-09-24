"""Deterministic shadow evaluation for Self-Learning RuleProposals."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from .rule_proposals import RuleProposal

ShadowOutcome = Literal["ACCEPT_FOR_GOVERNANCE", "REJECT", "INCONCLUSIVE"]


@dataclass(frozen=True)
class ShadowCase:
    case_id: str
    invariant_holds: bool
    expected_rejection: bool
    observed_rejection: bool


@dataclass(frozen=True)
class ShadowEvaluation:
    proposal_id: str
    outcome: ShadowOutcome
    cases_total: int
    cases_passed: int
    scope: str = "SELF_LEARNING_ONLY"

    def __post_init__(self) -> None:
        if self.scope != "SELF_LEARNING_ONLY":
            raise ValueError("shadow evaluation cannot authorize core mutation")


def evaluate_rule_shadow(proposal: RuleProposal, cases: tuple[ShadowCase, ...]) -> ShadowEvaluation:
    if proposal.mode != "SHADOW" or proposal.status != "PROPOSED":
        raise ValueError("only proposed shadow rules may be evaluated")
    if not cases:
        return ShadowEvaluation(proposal.proposal_id, "INCONCLUSIVE", 0, 0)
    passed = sum(
        case.invariant_holds == (not case.observed_rejection == case.expected_rejection)
        for case in cases
    )
    # A case passes when the proposal's expected decision matches the observed
    # decision. No execution or mutation occurs here.
    passed = sum(case.observed_rejection == case.expected_rejection for case in cases)
    if passed == len(cases):
        outcome: ShadowOutcome = "ACCEPT_FOR_GOVERNANCE"
    elif passed == 0:
        outcome = "REJECT"
    else:
        outcome = "INCONCLUSIVE"
    return ShadowEvaluation(proposal.proposal_id, outcome, len(cases), passed)
