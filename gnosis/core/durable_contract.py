"""Core contract for durable evolution boundaries.

Core defines what a durable evolution commit must prove. Storage adapters may
implement the contract, but they do not define Core semantics.
"""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class DurableEvolutionContract:
    cycle_id: str
    transition_id: str
    provenance_id: str
    audit_record_id: str

    def validate(self) -> None:
        values=(self.cycle_id,self.transition_id,self.provenance_id,self.audit_record_id)
        if any(not v for v in values): raise ValueError("durable evolution contract has empty identity")
        if len(set(values))!=len(values): raise ValueError("durable evolution identities must be unique")

    def required_links(self) -> tuple[tuple[str,str],...]:
        self.validate()
        return (
            ("cycle_id",self.cycle_id),
            ("transition_id",self.transition_id),
            ("provenance_id",self.provenance_id),
            ("audit_record_id",self.audit_record_id),
        )
