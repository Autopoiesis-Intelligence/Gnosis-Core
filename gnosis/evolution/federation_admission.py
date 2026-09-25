"""Core-owned admission boundary for already-validated Federation evidence."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from gnosis.evolution.provenance import EvidenceProvenance, build_provenance, canonical_digest
from registry.core_handoff import verify_handoff


@dataclass(frozen=True)
class FederationEvidenceEnvelope:
    handoff_sha256: str
    candidate_id: str
    source_id: str
    resource_id: str
    evidence_refs: tuple[str, ...]
    observations: Mapping[str, Any]


def admit_federation_evidence(
    handoff: Mapping[str, Any],
    observations: Mapping[str, Any],
) -> FederationEvidenceEnvelope:
    """Validate boundary integrity and return evidence only; never authorize commit."""
    checked = verify_handoff(dict(handoff))
    if checked.get("result") != "VALID":
        raise PermissionError("Federation handoff rejected")
    if not isinstance(observations, Mapping) or not observations:
        raise ValueError("Federation evidence observations are required")
    if handoff.get("candidate_id") == "" or handoff.get("source_id") == "":
        raise ValueError("Federation identity is incomplete")
    return FederationEvidenceEnvelope(
        handoff_sha256=str(handoff["handoff_sha256"]),
        candidate_id=str(handoff["candidate_id"]),
        source_id=str(handoff["source_id"]),
        resource_id=str(handoff["resource_id"]),
        evidence_refs=tuple(str(x) for x in handoff["evidence_refs"]),
        observations=dict(observations),
    )


def evidence_digest(envelope: FederationEvidenceEnvelope) -> str:
    return canonical_digest(envelope.observations)


def build_core_provenance(
    envelope: FederationEvidenceEnvelope,
    *,
    parent_state_id: str,
    parent_state_digest: str,
    proposed_state_digest: str,
    proposed_state_content_id: str,
    candidate_binding_digest: str,
    evaluation_status: str,
    shadow_status: str,
    invariant_status: str,
    governance_decision: str,
) -> EvidenceProvenance:
    """Build canonical Core provenance; does not commit or grant authority."""
    return build_provenance(
        candidate_id=envelope.candidate_id,
        parent_state_id=parent_state_id,
        parent_state_digest=parent_state_digest,
        proposed_state_digest=proposed_state_digest,
        proposed_state_content_id=proposed_state_content_id,
        candidate_binding_digest=candidate_binding_digest,
        observations=envelope.observations,
        evidence_digest=evidence_digest(envelope),
        evaluation_status=evaluation_status,
        shadow_status=shadow_status,
        invariant_status=invariant_status,
        governance_decision=governance_decision,
    )
