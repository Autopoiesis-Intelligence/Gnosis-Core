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
    trusted_policy_version: str | None = None,
    trusted_evidence_digest: str | None = None,
) -> None:
    """Validate against independently supplied trust anchors, then consume once.

    The trusted values must come from a production-controlled configuration or
    verifier, never from the request or AuthorizationValidity itself. Missing
    trust anchors fail closed. Callers must invoke this inside the same
    transaction that performs the eventual mutation.
    """
    validity = request.authorization_validity
    if not isinstance(validity, AuthorizationValidity):
        raise PermissionError("authorization validity is required")
    if validity.authorization_id != request.authorization.approval_id:
        raise PermissionError("authorization validity identity mismatch")
    if validity.revoked:
        raise PermissionError("authorization is revoked")
    if not trusted_policy_version or not trusted_evidence_digest:
        raise PermissionError("independent trusted execution policy is not configured")

    if trusted_evidence_digest != request.provenance.evidence_digest:
        raise PermissionError("trusted evidence digest does not match request provenance")

    validity.require_valid(
        expected_policy_version=trusted_policy_version,
        expected_evidence_digest=request.provenance.evidence_digest,
    )
    require_execution_commit(request)
    consume_authorization_in_transaction(
        conn,
        validity.authorization_id,
        request_provenance=request.request_provenance,
        evolution_identity=request.evolution_identity,
        policy_version=trusted_policy_version,
        actor=actor,
    )
