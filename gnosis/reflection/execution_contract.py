"""Neutral execution contract shared by authority and trusted execution boundaries.

This module contains only immutable request/identity validation primitives. It
must not depend on either authority issuance or the trusted execution gate,
so the dependency direction remains acyclic.
"""

from __future__ import annotations

from dataclasses import dataclass

from gnosis.evolution.provenance import canonical_digest

@dataclass(frozen=True)
class ExecutionAuthorization:
    """Authorization bound to one exact evolution provenance."""
    request_provenance: str
    owner_approved: bool = False
    evolution_identity: str = ""
    approval_id: str = ""

    @property
    def can_execute(self) -> bool:
        return (
            self.owner_approved
            and bool(self.request_provenance)
            and bool(self.evolution_identity)
        )



def require_execution_authorization(
    auth: ExecutionAuthorization | None,
    *,
    request_provenance: str,
    evolution_identity: str,
) -> None:
    """Fail closed unless authorization exactly matches the requested evolution."""
    if (
        auth is None
        or not auth.can_execute
        or auth.request_provenance != request_provenance
        or auth.evolution_identity != evolution_identity
    ):
        raise PermissionError("execution authorization does not match evolution")


@dataclass(frozen=True)
class ExecutionIntentSnapshot:
    """Immutable identity snapshot of the exact evolution authorized for execution."""
    provenance_id: str
    execution_id: str
    parent_state_id: str
    parent_state_digest: str
    evolution_identity: str
    candidate_binding_digest: str
    proposed_state_content_id: str

    @classmethod
    def from_provenance(cls, provenance: object) -> "ExecutionIntentSnapshot":
        return cls(
            provenance_id=str(provenance.provenance_id),
            execution_id=str(provenance.execution_id),
            parent_state_id=str(provenance.parent_state_id),
            parent_state_digest=str(provenance.parent_state_digest),
            evolution_identity=str(provenance.evolution_identity),
            candidate_binding_digest=str(provenance.candidate_binding_digest),
            proposed_state_content_id=str(provenance.proposed_state_content_id),
        )

    def matches_provenance(self, provenance: object) -> bool:
        return self == type(self).from_provenance(provenance)


def require_execution_intent_snapshot(
    snapshot: ExecutionIntentSnapshot | None,
    provenance: object,
) -> None:
    """Fail closed unless the immutable snapshot exactly matches current provenance."""
    if snapshot is None or not snapshot.matches_provenance(provenance):
        raise PermissionError("execution intent snapshot does not match evolution")


@dataclass(frozen=True)
class ExecutionCommitRequest:
    """All pre-commit identity material required for one authorized execution."""
    authorization: ExecutionAuthorization
    intent_snapshot: ExecutionIntentSnapshot
    request_provenance: str
    evolution_identity: str
    provenance: object
    authorization_validity: object


def _canonical_evolution_identity(provenance: object) -> str:
    """Recompute the identity instead of trusting a caller-supplied property."""
    return "evolution:" + canonical_digest({
        "candidate_id": str(provenance.candidate_id),
        "execution_id": str(provenance.execution_id),
        "parent_state_id": str(provenance.parent_state_id),
        "parent_state_digest": str(provenance.parent_state_digest),
        "proposed_state_digest": str(provenance.proposed_state_digest),
        "proposed_state_content_id": str(provenance.proposed_state_content_id),
        "candidate_binding_digest": str(provenance.candidate_binding_digest),
        "evidence_digest": str(provenance.evidence_digest),
        "evaluation_status": str(provenance.evaluation_status),
        "shadow_status": str(provenance.shadow_status),
        "invariant_status": str(provenance.invariant_status),
        "governance_decision": str(provenance.governance_decision),
        "provenance_id": str(provenance.provenance_id),
    })


def require_execution_commit(request: ExecutionCommitRequest) -> None:
    """Fail closed unless authorization, identity and freshness all agree."""
    require_execution_authorization(
        request.authorization,
        request_provenance=request.request_provenance,
        evolution_identity=request.evolution_identity,
    )
    if request.authorization.evolution_identity != request.intent_snapshot.evolution_identity:
        raise PermissionError("execution commit identity mismatch")
    if _canonical_evolution_identity(request.provenance) != request.evolution_identity:
        raise PermissionError("execution provenance identity is not canonical")
    require_execution_intent_snapshot(request.intent_snapshot, request.provenance)


def require_execution_integration_context(request: ExecutionCommitRequest, record: object) -> None:
    """Fail closed unless the authorized execution matches the integration context."""
    p = request.provenance
    for field in ("proposal_id", "version_id", "target"):
        request_value = getattr(p, field, None)
        record_value = getattr(record, field, None)
        if request_value is None:
            raise PermissionError(f"execution provenance has no integration field: {field}")
        if str(request_value) != str(record_value):
            raise PermissionError(f"execution integration context mismatch: {field}")


def require_execution_candidate_binding(
    request: ExecutionCommitRequest,
    candidate: object,
    record: object,
) -> None:
    """Bind the actually committed candidate and transition to the authorized provenance."""
    p = request.provenance
    candidate_id = str(getattr(candidate, "candidate_id", ""))
    if candidate_id != str(p.candidate_id):
        raise PermissionError("execution candidate does not match authorized provenance")

    parent_state_id = str(getattr(candidate, "parent_state_id", ""))
    if parent_state_id != str(p.parent_state_id):
        raise PermissionError("execution candidate parent does not match authorized provenance")

    parent_state_digest = str(p.parent_state_digest)
    binding_digest_fn = getattr(candidate, "binding_digest", None)
    if not callable(binding_digest_fn):
        raise PermissionError("execution candidate has no binding digest")
    if str(binding_digest_fn(parent_state_digest)) != str(p.candidate_binding_digest):
        raise PermissionError("execution candidate binding does not match authorized provenance")

    proposed_state = getattr(candidate, "proposed_state", None)
    if proposed_state is None:
        raise PermissionError("execution candidate has no proposed state")
    if str(getattr(proposed_state, "state_id", "")) != str(p.proposed_state_digest):
        raise PermissionError("execution candidate result does not match authorized evolution")
    if str(getattr(proposed_state, "content_id", "")) != str(p.proposed_state_content_id):
        raise PermissionError("execution candidate content does not match authorized evolution")

    if str(getattr(record, "candidate_id", "")) != candidate_id:
        raise PermissionError("transition record candidate does not match execution candidate")
    if str(getattr(record, "from_state_id", "")) != parent_state_id:
        raise PermissionError("transition record parent does not match execution candidate")
    if str(getattr(record, "to_state_id", "")) != str(p.proposed_state_digest):
        raise PermissionError("transition record result does not match authorized evolution")


