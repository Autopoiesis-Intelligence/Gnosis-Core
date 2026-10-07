"""Non-authoritative boundary for proposed Core evolution.

This module deliberately stops before activation. Governance can create a
request describing what would need explicit owner authorization, but the
request itself carries no execution capability and cannot mutate Core.
"""

from __future__ import annotations

from dataclasses import dataclass

from .governance import GovernanceDecision
from .crypto import verify_owner_authorization
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
    """Verified approval evidence from an external owner-authority boundary."""
    approval_id: str
    request_provenance: str
    evolution_identity: str
    authority_root: str
    scope: str
    policy_version: str
    evidence_digest: str
    signature: bytes
    owner_public_key: bytes

    @classmethod
    def from_signed_authorization(
        cls,
        authorization: dict[str, object],
        *,
        signature: bytes,
        owner_public_key: bytes,
    ) -> "OwnerApproval":
        if not verify_owner_authorization(owner_public_key, authorization, signature):
            raise PermissionError("owner authorization signature is invalid")
        return cls(
            approval_id=str(authorization["approval_id"]),
            request_provenance=str(authorization["request_provenance"]),
            evolution_identity=str(authorization["evolution_identity"]),
            authority_root=str(authorization["authority_root"]),
            scope=str(authorization["scope"]),
            policy_version=str(authorization["policy_version"]),
            evidence_digest=str(authorization["evidence_digest"]),
            signature=signature,
            owner_public_key=owner_public_key,
        )

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
    authorization_validity: object | None = None


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
        "evaluator_identity_ref": str(provenance.evaluator_identity_ref),
        "evaluator_identity_version": str(provenance.evaluator_identity_version),
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
