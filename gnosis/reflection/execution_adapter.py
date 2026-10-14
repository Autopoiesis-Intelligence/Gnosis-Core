"""Trusted execution adapter requiring signed owner proof before Core persistence."""
from __future__ import annotations

from gnosis.storage import load_state
from gnosis.storage.database import transaction
from gnosis.storage.repositories import _persist_transition_in_transaction
from gnosis.reflection.trusted_execution_gate import require_trusted_execution
from gnosis.reflection.authorization_consumption import consume_authorization_nonce_in_transaction
from gnosis.reflection.owner_authorization import ProductionAuthorization
from gnosis.reflection.production_trust_context import ProductionTrustContext
from gnosis.reflection.authority import ExecutionCommitRequest, ExecutionCommitResult, ExecutionReceipt, require_execution_candidate_binding


class SQLiteExecutionCommitAdapter:
    """Narrow persistence adapter: cryptographic authorization precedes mutation."""

    def commit(
        self, conn: object, instance: object, candidate: object, record: object,
        request: ExecutionCommitRequest, *, actor: str,
        production_authorization: ProductionAuthorization | None = None,
        trust_context: ProductionTrustContext | None = None,
    ) -> ExecutionCommitResult:
        if production_authorization is None or trust_context is None:
            raise PermissionError("signed production owner authorization is required")
        validity = request.authorization_validity
        if validity is None:
            raise PermissionError("authorization validity is required")
        with transaction(conn):
            expected_evidence_digest = trust_context.resolve_validity_evidence_digest(validity.authorization_id)
            trust_context.verify_commit(production_authorization, request, expected_evidence_digest=expected_evidence_digest)
            consume_authorization_nonce_in_transaction(
                conn, production_authorization.nonce,
                authorization_id=production_authorization.authorization_id, actor=actor,
            )
            require_trusted_execution(
                request, conn=conn, actor=actor,
                expected_policy_version=trust_context.policy_version,
                expected_evidence_digest=expected_evidence_digest,
            )
            require_execution_candidate_binding(request, candidate, record)
            if str(request.provenance.evolution_identity) != request.evolution_identity:
                raise PermissionError("execution commit identity mismatch")
            _persist_transition_in_transaction(conn, instance, candidate, record, actor=actor, failure_at=getattr(request, "failure_injection", None))
            resulting = load_state(conn, record.to_state_id)
            if resulting.state_id != str(request.provenance.proposed_state_digest):
                raise PermissionError("persisted resulting state does not match authorized evolution")
            receipt = ExecutionReceipt.after_commit(request, resulting)
            return ExecutionCommitResult(receipt=receipt, resulting_state_id=resulting.state_id)
