"""Verification and reassessment of Core counterexamples."""
from __future__ import annotations
from dataclasses import dataclass
from .gap import GapHypothesis
from .investigation import Counterexample

@dataclass(frozen=True)
class CounterexampleVerification:
    counterexample_id: str
    finding_id: str
    result: str
    evidence_refs: tuple[str, ...]
    reason: str

@dataclass(frozen=True)
class ReflectionReassessment:
    gap_id: str
    finding_id: str
    result: str
    verified_counterexamples: tuple[str, ...]
    unresolved: bool

def verify_counterexample(counterexample: Counterexample, *, refutes: bool, reason: str) -> CounterexampleVerification:
    if counterexample.status != "ADMITTED":
        raise ValueError("only admitted counterexamples can be verified")
    if not counterexample.evidence_refs:
        raise ValueError("counterexample verification requires evidence")
    result = "REFUTES" if refutes else "DOES_NOT_REFUTE"
    return CounterexampleVerification(counterexample.counterexample_id,counterexample.finding_id,result,counterexample.evidence_refs,reason)

def reassess_gap(gap: GapHypothesis, finding_id: str, verifications: tuple[CounterexampleVerification, ...]) -> ReflectionReassessment:
    if finding_id.removeprefix("finding:") != gap.gap_id.removeprefix("gap:"):
        raise ValueError("finding/gap identity mismatch")
    verified = tuple(v.counterexample_id for v in verifications if v.finding_id == finding_id and v.result == "REFUTES")
    if verified:
        return ReflectionReassessment(gap.gap_id,finding_id,"REFUTED",verified,False)
    if any(v.result == "DOES_NOT_REFUTE" for v in verifications):
        return ReflectionReassessment(gap.gap_id,finding_id,"UNRESOLVED",(),True)
    return ReflectionReassessment(gap.gap_id,finding_id,"INCONCLUSIVE",(),True)
