"""Composable pre-commit gate; does not own Core mutation or persistence."""
from __future__ import annotations

from gnosis.reflection.authorization_consumption import consume_authorization_in_transaction
from gnosis.reflection.authorization_validity import AuthorizationValidity
from gnosis.reflection.authority import ExecutionCommitRequest, require_execution_commit


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
    if validity.policy_version == "":
        raise PermissionError("authorization policy is missing")
    provenance_evidence = str(getattr(request.provenance, "evidence_digest", ""))
    if not provenance_evidence:
        raise PermissionError("execution provenance evidence is missing")
    if validity.validity_evidence_digest != provenance_evidence:
        raise PermissionError("authorization validity evidence mismatch")
    validity.require_valid(
        expected_policy_version=validity.policy_version,
        expected_evidence_digest=provenance_evidence,
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
