"""Non-authoritative boundary for proposed Core evolution.

This module deliberately stops before activation. Governance can create a
request describing what would need explicit owner authorization, but the
request itself carries no execution capability and cannot mutate Core.
"""

from __future__ import annotations

from dataclasses import dataclass

from .governance import GovernanceDecision
from gnosis.evolution.provenance import canonical_digest
from gnosis.storage import load_state
from gnosis.storage.repositories import _persist_transition


@dataclass(frozen=True)
class AuthorityRequest:
    """A request for explicit authorization, not an authorization token."""

    decision: str
    rationale: tuple[str, ...]
    provenance: str = "reflection-authority-boundary"
    requires_owner_approval: bool = True

    @property
    def authorized(self) -> bool:
        """The request itself never grants authority."""
        return False

    @property
    def can_activate(self) -> bool:
        """No activation capability crosses this boundary."""
        return False

    @property
    def can_rollback(self) -> bool:
        """No rollback capability crosses this boundary."""
        return False


def request_authorization(decision: GovernanceDecision) -> AuthorityRequest:
    """Translate a governance classification into an explicit approval request."""
    return AuthorityRequest(
        decision=decision.decision,
        rationale=decision.rationale,
    )


@dataclass(frozen=True)
class OwnerApproval:
    """Opaque approval evidence from an external owner-authority boundary."""
    approval_id: str
    request_provenance: str
    evolution_identity: str


def issue_execution_authorization(
    approval: OwnerApproval | None,
    *,
    request_provenance: str,
    evolution_identity: str,
) -> ExecutionAuthorization:
    """Refuse boolean-only approval; real owner issuer remains an explicit boundary."""
    if (
        approval is None
        or not approval.approval_id
        or approval.request_provenance != request_provenance
        or approval.evolution_identity != evolution_identity
    ):
        raise PermissionError("owner approval does not match evolution")
    raise NotImplementedError("trusted owner-authority issuer is not implemented")


from .execution_contract import (
    ExecutionAuthorization,
    ExecutionCommitRequest,
    ExecutionIntentSnapshot,
    _canonical_evolution_identity,
    require_execution_authorization,
    require_execution_candidate_binding,
    require_execution_commit,
    require_execution_intent_snapshot,
    require_execution_integration_context,
)

@dataclass(frozen=True)
class ExecutionReceipt:
    """Immutable evidence produced only after a caller supplies a committed result digest."""
    execution_id: str
    provenance_id: str
    evolution_identity: str
    parent_state_digest: str
    resulting_state_digest: str
    candidate_binding_digest: str

    @property
    def receipt_id(self) -> str:
        """Canonical identity of this immutable execution evidence."""
        return "sha256:" + canonical_digest({
            "execution_id": self.execution_id,
            "provenance_id": self.provenance_id,
            "evolution_identity": self.evolution_identity,
            "parent_state_digest": self.parent_state_digest,
            "resulting_state_digest": self.resulting_state_digest,
            "candidate_binding_digest": self.candidate_binding_digest,
        })

    @classmethod
    def after_commit(cls, request: ExecutionCommitRequest, resulting_state: object) -> "ExecutionReceipt":
        require_execution_commit(request)
        resulting_state_digest = str(getattr(resulting_state, "state_id", canonical_digest(resulting_state)))
        if not resulting_state_digest:
            raise ValueError("resulting state digest is required for an execution receipt")
        p = request.provenance
        if str(p.proposed_state_digest) != resulting_state_digest:
            raise PermissionError("resulting state does not match authorized evolution")
        return cls(
            execution_id=str(p.execution_id),
            provenance_id=str(p.provenance_id),
            evolution_identity=str(p.evolution_identity),
            parent_state_digest=str(p.parent_state_digest),
            resulting_state_digest=str(resulting_state_digest),
            candidate_binding_digest=str(p.candidate_binding_digest),
        )

    def matches_request(self, request: ExecutionCommitRequest) -> bool:
        p = request.provenance
        return (
            self.execution_id == str(p.execution_id)
            and self.provenance_id == str(p.provenance_id)
            and self.evolution_identity == str(p.evolution_identity)
            and self.parent_state_digest == str(p.parent_state_digest)
            and self.resulting_state_digest == str(p.proposed_state_digest)
            and self.candidate_binding_digest == str(p.candidate_binding_digest)
            and request.authorization.evolution_identity == self.evolution_identity
        )


def require_execution_receipt(receipt: ExecutionReceipt | None, request: ExecutionCommitRequest) -> None:
    """Fail closed unless a post-commit receipt is bound to the authorized evolution."""
    if receipt is None or not receipt.resulting_state_digest or not receipt.matches_request(request):
        raise PermissionError("execution receipt does not match committed evolution")


@dataclass(frozen=True)
class ExecutionCommitResult:
    receipt: ExecutionReceipt
    resulting_state_id: str


class SQLiteExecutionCommitAdapter:
    """Narrow persistence adapter: authorization is checked before durable mutation."""

    def commit(self, conn: object, instance: object, candidate: object, record: object, request: ExecutionCommitRequest, *, actor: str, failure_at: str|None = None) -> ExecutionCommitResult:
        from gnosis.storage.database import transaction
        from gnosis.reflection.trusted_execution_gate import require_trusted_execution, AuthorizationValidity
        # Non-mutating preflight: reject malformed/unauthorized requests before
        # opening a transaction. Authorization consumption remains transactional.
        if not isinstance(request.authorization_validity, AuthorizationValidity):
            raise PermissionError("authorization validity is required")
        request.authorization_validity.require_valid(
            expected_policy_version=request.authorization_validity.policy_version,
            expected_evidence_digest=request.authorization_validity.validity_evidence_digest,
        )
        require_execution_commit(request)
        require_execution_candidate_binding(request, candidate, record)
        with transaction(conn):
            require_trusted_execution(request, conn=conn, actor=actor)
            require_execution_candidate_binding(request, candidate, record)
            if str(request.provenance.evolution_identity) != request.evolution_identity:
                raise PermissionError("execution commit identity mismatch")
            from gnosis.storage.repositories import _persist_transition_in_transaction
            _persist_transition_in_transaction(conn, instance, candidate, record, actor=actor, failure_at=failure_at)
            resulting = load_state(conn, record.to_state_id)
            if resulting.state_id != str(request.provenance.proposed_state_digest):
                raise PermissionError("persisted resulting state does not match authorized evolution")
            receipt = ExecutionReceipt.after_commit(request, resulting)
            return ExecutionCommitResult(receipt=receipt, resulting_state_id=resulting.state_id)
