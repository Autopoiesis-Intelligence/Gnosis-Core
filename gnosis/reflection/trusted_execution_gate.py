"""Composable pre-commit gate; does not own Core mutation or persistence."""
from __future__ import annotations

from typing import TYPE_CHECKING

from gnosis.reflection.authorization_consumption import consume_authorization_in_transaction
from gnosis.reflection.authorization_validity import AuthorizationValidity
from gnosis.reflection.authority import require_execution_commit

if TYPE_CHECKING:
    from gnosis.reflection.authority import ExecutionCommitRequest


def require_trusted_execution(
    request: ExecutionCommitRequest,
    *,
    conn: object,
    actor: str,
) -> None:
    """Validate request-bound authorization, consume it once, then run canonical Core gate.

    The caller must invoke this inside the same transaction that performs the
    eventual mutation. This function itself never mutates Core state.
    """
    validity = request.authorization_validity
    if not isinstance(validity, AuthorizationValidity):
        raise PermissionError("authorization validity is required")
    if validity.authorization_id != request.authorization.approval_id:
        raise PermissionError("authorization validity identity mismatch")
    evaluated_policy = getattr(request.provenance, "evaluated_policy", None)
    if evaluated_policy is None:
        raise PermissionError("evaluated policy identity is missing")
    if request.authorization.policy_identity != evaluated_policy:
        raise PermissionError("authorization evaluated policy mismatch")
    if validity.policy_identity != evaluated_policy:
        raise PermissionError("authorization validity evaluated policy mismatch")
    if validity.policy_version == "":
        raise PermissionError("authorization policy is missing")
    validity.require_valid(
        expected_policy_version=validity.policy_version,
        expected_evidence_digest=validity.validity_evidence_digest,
        expected_policy_identity=evaluated_policy,
    )
    require_execution_commit(request)
    consume_authorization_in_transaction(
        conn,
        validity.authorization_id,
        request_provenance=request.request_provenance,
        evolution_identity=request.evolution_identity,
        policy_version=validity.policy_version,
        actor=actor,
    )
