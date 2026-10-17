"""Fail-closed pre-commit gate until trusted owner issuance is integrated."""
from __future__ import annotations

from typing import TYPE_CHECKING

from gnosis.reflection.authorization_validity import AuthorizationValidity

if TYPE_CHECKING:
    from gnosis.reflection.authority import ExecutionCommitRequest


def require_trusted_execution(
    request: ExecutionCommitRequest,
    *,
    conn: object,
    actor: str,
) -> None:
    """Reject all execution requests until an independent trust source is wired.

    The caller must invoke this inside the transaction that would perform the
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

    # Field equality among caller-controlled values does not establish issuer
    # authority. Fail closed before consumption, audit append, or state mutation.
    raise PermissionError(
        "trusted owner-authority verifier is not configured; execution blocked"
    )
