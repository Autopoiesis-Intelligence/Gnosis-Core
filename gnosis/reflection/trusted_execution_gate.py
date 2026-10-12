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
    expected_policy_version: str,
    expected_evidence_digest: str,
) -> None:
    """Validate authorization against policy supplied by an independent trust boundary.

    The caller must provide expected_policy_version from trusted configuration;
    it must not be copied from the request or its validity record. The caller
    must invoke this inside the same transaction that performs the mutation.
    """
    if not expected_policy_version:
        raise PermissionError("trusted expected policy version is required")
    if not expected_evidence_digest:
        raise PermissionError("trusted expected validity evidence digest is required")
    validity = request.authorization_validity
    if not isinstance(validity, AuthorizationValidity):
        raise PermissionError("authorization validity is required")
    if validity.authorization_id != request.authorization.approval_id:
        raise PermissionError("authorization validity identity mismatch")
    validity.require_valid(
        expected_policy_version=expected_policy_version,
        expected_evidence_digest=expected_evidence_digest,
    )
    require_execution_commit(request)
    consume_authorization_in_transaction(
        conn,
        validity.authorization_id,
        request_provenance=request.request_provenance,
        evolution_identity=request.evolution_identity,
        policy_version=expected_policy_version,
        actor=actor,
    )
