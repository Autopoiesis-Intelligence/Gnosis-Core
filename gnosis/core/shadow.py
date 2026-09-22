"""Core shadow evaluation boundary for rule proposals."""
from __future__ import annotations
from dataclasses import dataclass
from .rule_proposal import RuleProposal

@dataclass(frozen=True)
class ShadowEvaluation:
    evaluation_id: str
    proposal_id: str
    state_id: str
    status: str
    passed_checks: tuple[str, ...]
    failed_checks: tuple[str, ...]
    regressions: tuple[str, ...] = ()
    provenance: str = "core-shadow"

def evaluate_rule_proposal(
    proposal: RuleProposal,
    *,
    state_id: str,
    checks: tuple[tuple[str, bool], ...],
) -> ShadowEvaluation:
    if proposal.status != "PROPOSED":
        raise ValueError("only proposed rules can enter shadow evaluation")
    passed = tuple(name for name, ok in checks if ok)
    failed = tuple(name for name, ok in checks if not ok)
    regressions = tuple(name for name in failed if name.startswith("regression:"))
    status = "PASS" if not failed else "FAIL"
    return ShadowEvaluation(
        evaluation_id="shadow:"+proposal.proposal_id.removeprefix("rule:"),
        proposal_id=proposal.proposal_id,
        state_id=state_id,
        status=status,
        passed_checks=passed,
        failed_checks=failed,
        regressions=regressions,
    )
