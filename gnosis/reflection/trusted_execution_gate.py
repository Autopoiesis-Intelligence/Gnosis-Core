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
    """Validate request-bound fields and fail closed until trusted issuance exists.

    The caller must invoke this inside the same transaction that performs the
    eventual mutation. This function itself never mutates Core state.

    SECURITY CONTAINMENT:
    The current production path has no independently verifiable issuer proof
    or protected trust-root provider. Caller-constructed ExecutionAuthorization
    and AuthorizationValidity objects are not evidence of owner authority.
    Therefore a structurally valid request is rejected before Core admission
    or authorization consumption. Remove this block only when an independently
    configured verifier is integrated and its trust source is proven.
    """
    validity = request.authorization_validity
    if not isinstance(validity, AuthorizationValidity):
        raise PermissionError("authorization validity is required")
    if validity.authorization_id != request.authorization.approval_id:
        raise PermissionError("authorization validity identity mismatch")
    if validity.policy_version == "":
        raise PermissionError("authorization policy is missing")
    validity.require_valid(
        expected_policy_version=validity.policy_version,
        expected_evidence_digest=validity.validity_evidence_digest,
    )

    # Fail closed: comparing fields from the same caller-controlled request
    # does not prove issuer authority. No consumption event may be written.
    raise PermissionError(
        "trusted owner-authority verifier is not configured; execution blocked"
    )

    # Intentionally unreachable until the production verifier is implemented.
    require_execution_commit(request)
    consume_authorization_in_transaction(
        conn,
        validity.authorization_id,
        request_provenance=request.request_provenance,
        evolution_identity=request.evolution_identity,
        policy_version=validity.policy_version,
        actor=actor,
    )
