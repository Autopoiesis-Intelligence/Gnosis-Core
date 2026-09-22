"""Canonical identity matrix for evolution objects."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class IdentityContract:
    name: str
    primary_identity: str
    content_identity: str
    persistence_identity: str
    lineage_binding: str
    evidence_binding: str

IDENTITY_MATRIX = (
    IdentityContract("State","state_id","content_id","state_digest","parent/transition state_id","candidate binding"),
    IdentityContract("Candidate","candidate_id","proposed_state_content_id","candidate_binding_digest","parent_state_id","provenance candidate_id"),
    IdentityContract("Transition","transition_id","TransitionRecord","transition_id","from_state_id→to_state_id","provenance/evidence"),
    IdentityContract("Provenance","provenance_id","evolution identity","provenance_id","parent_state_id→proposed_state","evidence_digest"),
    IdentityContract("RecoveryCheckpoint","transition_id+state_id","checkpoint tuple","state_digest+audit_sequence","canonical lineage","verified evolution graph"),
)
