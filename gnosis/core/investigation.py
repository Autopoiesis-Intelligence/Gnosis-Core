"""Canonical Core investigation requests and counterexample admission."""
from __future__ import annotations
from dataclasses import dataclass
from .reflection import ReflectionFinding

@dataclass(frozen=True)
class Counterexample:
    counterexample_id: str
    finding_id: str
    description: str
    evidence_refs: tuple[str, ...] = ()
    status: str = "PROPOSED"

@dataclass(frozen=True)
class Investigation:
    investigation_id: str
    finding_id: str
    target: str
    required_variations: tuple[str, ...]
    status: str = "OPEN"

    @classmethod
    def from_finding(cls, finding: ReflectionFinding) -> "Investigation":
        if finding.status != "OPEN":
            raise ValueError("only OPEN findings can start investigation")
        return cls(
            investigation_id="investigation:"+finding.finding_id.removeprefix("finding:"),
            finding_id=finding.finding_id,
            target=finding.statement,
            required_variations=("state", "candidate", "execution", "source"),
        )

def admit_counterexample(investigation: Investigation, counterexample: Counterexample) -> Counterexample:
    if counterexample.finding_id != investigation.finding_id:
        raise ValueError("counterexample/finding identity mismatch")
    if investigation.status != "OPEN":
        raise ValueError("investigation is not open")
    if not counterexample.evidence_refs:
        raise ValueError("counterexample requires evidence references")
    return Counterexample(counterexample.counterexample_id,counterexample.finding_id,counterexample.description,counterexample.evidence_refs,"ADMITTED")
