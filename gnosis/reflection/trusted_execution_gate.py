"""Composable pre-commit gate; does not own Core mutation or persistence."""
from __future__ import annotations

from typing import TYPE_CHECKING

from gnosis.reflection.authorization_consumption import consume_authorization_in_transaction
from gnosis.reflection.authorization_validity import AuthorizationValidity
from gnosis.reflection.authority import require_execution_commit

if TYPE_CHECKING:
    from gnosis.reflection.authority import ExecutionCommitRequest


# Trusted policy pin owned by the execution boundary. This deliberately does
# not come from AuthorizationValidity or ExecutionCommitRequest, both of which
# are request-bound data. A future deployment-config provider must preserve
# this independent trust boundary rather than accepting a caller-supplied value.
TRUSTED_EXECUTION_POLICY_VERSION = "policy-1"


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
    if not TRUSTED_EXECUTION_POLICY_VERSION:
        raise PermissionError("trusted execution policy is not configured")
    validity.require_valid(
        expected_policy_version=TRUSTED_EXECUTION_POLICY_VERSION,
        expected_evidence_digest=validity.validity_evidence_digest,
    )
    require_execution_commit(request)
    consume_authorization_in_transaction(
        conn,
        validity.authorization_id,
        request_provenance=request.request_provenance,
        evolution_identity=request.evolution_identity,
        policy_version=TRUSTED_EXECUTION_POLICY_VERSION,
        actor=actor,
    )
