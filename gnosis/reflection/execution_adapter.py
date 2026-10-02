"""Trusted execution adapter boundary for authorized Core persistence."""
from __future__ import annotations

from gnosis.storage import load_state
from gnosis.storage.database import transaction
from gnosis.storage.repositories import _persist_transition_in_transaction
from gnosis.evolution.provenance import canonical_digest
from gnosis.reflection.trusted_execution_gate import require_trusted_execution
from gnosis.reflection.authority import (
    ExecutionCommitRequest,
    ExecutionCommitResult,
    ExecutionReceipt,
    require_execution_candidate_binding,
)


class SQLiteExecutionCommitAdapter:
    """Narrow persistence adapter: authorization is checked before durable mutation."""

    def commit(self, conn: object, instance: object, candidate: object, record: object, request: ExecutionCommitRequest, *, actor: str, governed_context: object) -> ExecutionCommitResult:
        if governed_context is None or not getattr(governed_context, "scope_lock_id", "") or not getattr(governed_context, "environment_attestation_id", ""):
            raise PermissionError("governed execution context is required before persistence")
        if governed_context.evolution_identity != request.evolution_identity:
            raise PermissionError("governed context evolution identity mismatch")
        if governed_context.provenance_id != str(request.provenance.provenance_id):
            raise PermissionError("governed context provenance mismatch")
        record_fields = {
            "integration_id": str(getattr(record, "integration_id", "")),
            "version_id": str(getattr(record, "version_id", "")),
            "target": str(getattr(record, "target", "")),
            "action": str(getattr(record, "action", "")),
        }
        mutation_id = "sha256:" + canonical_digest(record_fields)
        expected_binding = "sha256:" + canonical_digest({
            "mutation_id": mutation_id,
            "integration_id": record_fields["integration_id"],
            "version_id": record_fields["version_id"],
            "evolution_identity": request.evolution_identity,
        })
        if governed_context.proposal_binding_digest != expected_binding:
            raise PermissionError("governed context proposal binding mismatch")
        with transaction(conn):
            require_trusted_execution(request, conn=conn, actor=actor)
            require_execution_candidate_binding(request, candidate, record)
            if str(request.provenance.evolution_identity) != request.evolution_identity:
                raise PermissionError("execution commit identity mismatch")
            _persist_transition_in_transaction(conn, instance, candidate, record, actor=actor, failure_at=getattr(request, "failure_injection", None))
            resulting = load_state(conn, record.to_state_id)
            if resulting.state_id != str(request.provenance.proposed_state_digest):
                raise PermissionError("persisted resulting state does not match authorized evolution")
            receipt = ExecutionReceipt.after_commit(request, resulting)
            return ExecutionCommitResult(receipt=receipt, resulting_state_id=resulting.state_id)

