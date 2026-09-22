"""Core-side durable commit contract and canonical authorized-transition bridge."""
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
    def persist_evolution(
        self,
        provenance: EvidenceProvenance,
        *,
        event_type: str,
        payload: Mapping[str, Any],
    ) -> DurableCommitResult: ...


def durable_commit(
    port: PersistencePort,
    provenance: EvidenceProvenance,
    *,
    event_type: str,
    payload: Mapping[str, Any],
    actor: str = "core",
    failure_at: str | None = None,
) -> DurableCommitResult:
    if not event_type:
        raise ValueError("event_type is required")
    if not isinstance(payload, Mapping):
        raise TypeError("payload must be a mapping")
    return port.persist_evolution(
        provenance,
        event_type=event_type,
        payload=dict(payload),
    )


def persist_authorized_transition(
    conn_or_port: Any,
    authorization: Any,
    proposal: Any,
    instance: Any,
    candidate: Any,
    transition: Any,
    *,
    actor: str = "core",
    failure_at: str | None = None,
) -> Any:
    """Canonical entrypoint; storage execution is delegated to the durable adapter."""
    if hasattr(conn_or_port, "execute"):
        from gnosis.storage.durable_commit_adapter import persist_authorized_transition as adapter
        return adapter(
            conn_or_port,
            authorization,
            proposal,
            instance,
            candidate,
            transition,
            actor=actor,
            failure_at=failure_at,
        )
    return durable_commit(
        conn_or_port,
        authorization,
        event_type="authorized_transition",
        payload={
            "proposal_id": getattr(proposal, "proposal_id", ""),
            "candidate_id": getattr(candidate, "candidate_id", ""),
            "transition_id": getattr(transition, "candidate_id", ""),
        },
        actor=actor,
        failure_at=failure_at,
    )
