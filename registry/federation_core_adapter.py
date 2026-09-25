"""Thin Federation -> existing Core authority adapter.

This module validates a non-authoritative handoff and maps only its identity
references into the existing Core execution contract. It creates no Core
mutation capability and no second state model.
"""
from __future__ import annotations

from dataclasses import dataclass

from registry.core_handoff import verify_handoff


@dataclass(frozen=True)
class FederationCoreBinding:
    handoff_sha256: str
    candidate_id: str
    source_id: str
    resource_id: str
    target: str
    action: str
    evidence_refs: tuple[str, ...]


def bind_handoff_to_core(handoff: dict) -> FederationCoreBinding:
    verified = verify_handoff(handoff)
    if verified.get("result") != "VALID":
        raise PermissionError("Federation handoff is not valid")
    return FederationCoreBinding(
        handoff_sha256=str(handoff["handoff_sha256"]),
        candidate_id=str(handoff["candidate_id"]),
        source_id=str(handoff["source_id"]),
        resource_id=str(handoff["resource_id"]),
        target=str(handoff["target"]),
        action=str(handoff["action"]),
        evidence_refs=tuple(handoff["evidence_refs"]),
    )


def core_identity_fields(binding: FederationCoreBinding) -> dict[str, object]:
    """Return identity material only; Core remains responsible for authority."""
    return {
        "candidate_id": binding.candidate_id,
        "source_id": binding.source_id,
        "resource_id": binding.resource_id,
        "target": binding.target,
        "action": binding.action,
        "evidence_refs": binding.evidence_refs,
    }
