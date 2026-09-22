"""Support qualification and proposal boundary for Core reflection."""
from __future__ import annotations
from dataclasses import dataclass
from .counterexample import ReflectionReassessment
from .gap import GapHypothesis

@dataclass(frozen=True)
class RuleProposal:
    proposal_id: str
    gap_id: str
    finding_id: str
    source_records: tuple[str, ...]
    rationale: str
    status: str = "PROPOSED"
    provenance: str = "core-reflection"

def qualify_supported(reassessment: ReflectionReassessment, gap: GapHypothesis) -> ReflectionReassessment:
    if reassessment.gap_id != gap.gap_id:
        raise ValueError("reassessment/gap identity mismatch")
    if reassessment.result not in {"UNRESOLVED", "INCONCLUSIVE"}:
        return reassessment
    if reassessment.verified_counterexamples:
        return reassessment
    return ReflectionReassessment(gap.gap_id,reassessment.finding_id,"SUPPORTED",(),True)

def make_rule_proposal(reassessment: ReflectionReassessment, gap: GapHypothesis) -> RuleProposal:
    if reassessment.gap_id != gap.gap_id:
        raise ValueError("reassessment/gap identity mismatch")
    if reassessment.result != "SUPPORTED":
        raise ValueError("only supported findings can create rule proposals")
    return RuleProposal(
        proposal_id="rule:"+gap.gap_id.removeprefix("gap:"),
        gap_id=gap.gap_id,
        finding_id=reassessment.finding_id,
        source_records=gap.source_records,
        rationale=gap.description,
    )
