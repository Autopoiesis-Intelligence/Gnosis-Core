"""Bind runtime lineage to concrete Core artifacts and durable transition IDs."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class DomainLineage:
    cycle_id: str
    gap_id: str
    investigation_id: str
    proposal_id: str
    evaluation_id: str
    authorization_id: str
    transition_id: str

    def validate(self) -> None:
        values = (
            self.cycle_id, self.gap_id, self.investigation_id,
            self.proposal_id, self.evaluation_id,
            self.authorization_id, self.transition_id,
        )
        if any(not value for value in values):
            raise ValueError("domain lineage contains empty identity")
        if len(set(values)) != len(values):
            raise ValueError("domain lineage identities must be unique")

    def refs(self) -> tuple[str, ...]:
        self.validate()
        return (
            self.gap_id, self.investigation_id, self.proposal_id,
            self.evaluation_id, self.authorization_id, self.transition_id,
        )

def bind_domain_lineage(
    *,
    cycle_id: str,
    gap_id: str,
    investigation_id: str,
    proposal_id: str,
    evaluation_id: str,
    authorization_id: str,
    transition_id: str,
) -> DomainLineage:
    lineage = DomainLineage(
        cycle_id, gap_id, investigation_id, proposal_id,
        evaluation_id, authorization_id, transition_id,
    )
    lineage.validate()
    return lineage
