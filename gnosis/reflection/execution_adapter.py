"""Trusted execution adapter boundary for authorized Core persistence."""
from __future__ import annotations

from gnosis.storage import load_state
from gnosis.storage.database import transaction
from gnosis.storage.repositories import _persist_transition_in_transaction
from gnosis.reflection.trusted_execution_gate import require_trusted_execution
from gnosis.reflection.authority import (
    ExecutionCommitRequest,
    ExecutionCommitResult,
    ExecutionReceipt,
    require_execution_candidate_binding,
)


class SQLiteExecutionCommitAdapter:
    """Narrow persistence adapter: authorization is checked before durable mutation."""

    def commit(self, conn: object, instance: object, candidate: object, record: object, request: ExecutionCommitRequest, *, actor: str) -> ExecutionCommitResult:
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

