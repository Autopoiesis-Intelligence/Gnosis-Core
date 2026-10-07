"""Composable pre-commit gate; does not own Core mutation or persistence."""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from gnosis.reflection.authorization_consumption import consume_authorization_in_transaction
from gnosis.reflection.authorization_validity import AuthorizationValidity
from gnosis.reflection.authority import require_execution_commit

if TYPE_CHECKING:
    from gnosis.reflection.authority import ExecutionCommitRequest


@dataclass(frozen=True)
class TrustedExecutionContext:
    """Trusted, caller-independent execution policy context."""
    policy_version: str
    policy_binding_digest: str = ""

    def require_valid(self, validity: AuthorizationValidity) -> None:
        if not self.policy_version:
            raise PermissionError("trusted execution policy is missing")
        if validity.policy_version != self.policy_version:
            raise PermissionError("authorization policy does not match trusted execution policy")
        if self.policy_binding_digest and validity.validity_evidence_digest != self.policy_binding_digest:
            raise PermissionError("authorization evidence does not match trusted policy binding")


def require_trusted_execution(
    request: ExecutionCommitRequest,
    *,
    conn: object,
    actor: str,
    trusted_context: TrustedExecutionContext | None = None,
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
    if trusted_context is None:
        raise PermissionError("trusted execution context is required")
    trusted_context.require_valid(validity)
    validity.require_valid(
        expected_policy_version=trusted_context.policy_version,
        expected_evidence_digest=validity.validity_evidence_digest,
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
