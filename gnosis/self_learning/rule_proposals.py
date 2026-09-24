"""Shadow-only RuleProposal generation from self-learning counterexamples."""

from __future__ import annotations

from dataclasses import dataclass
from .collaboration_evidence import EvidenceCounterexample


@dataclass(frozen=True)
class RuleProposal:
    proposal_id: str
    source_counterexample_id: str
    invariant: str
    rule_text: str
    scope: str = "SELF_LEARNING_ONLY"
    mode: str = "SHADOW"
    status: str = "PROPOSED"

    def __post_init__(self) -> None:
        if self.scope != "SELF_LEARNING_ONLY":
            raise ValueError("rule proposal cannot authorize core mutation")
        if self.mode != "SHADOW":
            raise ValueError("rule proposal must start in shadow mode")
        if self.status != "PROPOSED":
            raise ValueError("new rule proposal must start as proposed")
        if not self.proposal_id or not self.source_counterexample_id or not self.rule_text:
            raise ValueError("rule proposal identity and text are required")


def propose_rule(counterexample: EvidenceCounterexample) -> RuleProposal:
    """Turn a counterexample into a deterministic, non-authorizing proposal."""
    rule_text = (
        f"Preserve immutable evidence per execution attempt; reject conflicting "
        f"observations for the same attempt ({counterexample.invariant})."
    )
    proposal_id = "ruleproposal:" + counterexample.fingerprint.split(":", 1)[1]
    return RuleProposal(
        proposal_id=proposal_id,
        source_counterexample_id=counterexample.counterexample_id,
        invariant=counterexample.invariant,
        rule_text=rule_text,
    )
