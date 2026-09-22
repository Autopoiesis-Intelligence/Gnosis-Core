"""Canonical Core governance gate for proposed evolution."""
from __future__ import annotations
from dataclasses import dataclass
from .rule_proposal import RuleProposal
from .shadow import ShadowEvaluation

@dataclass(frozen=True)
class AuthorizationPackage:
    authorization_id: str
    proposal_id: str
    evidence_refs: tuple[str, ...]
    counterexample_refs: tuple[str, ...]
    shadow_evaluation_id: str
    decision: str
    limitations: tuple[str, ...] = ()
    provenance: str = "core-governance"

def authorize(
    proposal: RuleProposal,
    shadow: ShadowEvaluation,
    *,
    evidence_refs: tuple[str, ...],
    counterexample_refs: tuple[str, ...] = (),
    limitations: tuple[str, ...] = (),
) -> AuthorizationPackage:
    if proposal.status != "PROPOSED":
        raise ValueError("only proposed rules can enter governance")
    if shadow.proposal_id != proposal.proposal_id:
        raise ValueError("proposal/shadow identity mismatch")
    if shadow.status != "PASS":
        raise ValueError("only passing shadow evaluations can enter authorization")
    if not evidence_refs:
        raise ValueError("authorization requires evidence references")
    return AuthorizationPackage(
        authorization_id="auth:"+proposal.proposal_id.removeprefix("rule:"),
        proposal_id=proposal.proposal_id,
        evidence_refs=evidence_refs,
        counterexample_refs=counterexample_refs,
        shadow_evaluation_id=shadow.evaluation_id,
        decision="AUTHORIZED",
        limitations=limitations,
    )
