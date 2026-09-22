"""Core-side durable commit contract; storage-neutral."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Mapping, Protocol
from .audit import EvolutionAuditRecord
from .provenance import EvidenceProvenance

@dataclass(frozen=True)
class DurableCommitResult:
    provenance_id: str
    audit_record: EvolutionAuditRecord

class PersistencePort(Protocol):
    def persist_evolution(self, provenance: EvidenceProvenance, *, event_type: str,
                          payload: Mapping[str, Any]) -> DurableCommitResult: ...

def durable_commit(port: PersistencePort, provenance: EvidenceProvenance, *,
                   event_type: str, payload: Mapping[str, Any], actor: str = "core", failure_at: str | None = None) -> DurableCommitResult:
    if not event_type:
        raise ValueError("event_type is required")
    if not isinstance(payload, Mapping):
        raise TypeError("payload must be a mapping")
    try:\n        return port.persist_evolution(provenance, event_type=event_type, payload=dict(payload))\n    except AttributeError:\n        raise TypeError("persistence port must implement persist_evolution")


def persist_authorized_transition(
    port: PersistencePort,
    provenance: EvidenceProvenance,
    *,
    payload: Mapping[str, Any],
) -> DurableCommitResult:
    """Canonical persistence entrypoint for an already-authorized transition."""
    return durable_commit(
        port,
        provenance,
        event_type="authorized_transition",
        payload=payload,
    )
