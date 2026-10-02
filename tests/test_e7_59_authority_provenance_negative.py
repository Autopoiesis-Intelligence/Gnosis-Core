import pytest

from gnosis.reflection.authorization_validity import AuthorizationValidity
from gnosis.reflection.authority import (
    ExecutionAuthorization,
    ExecutionCommitRequest,
    ExecutionIntentSnapshot,
)
from gnosis.reflection.trusted_execution_gate import require_trusted_execution


def test_caller_created_authorization_is_rejected_without_trusted_issuer(
    sqlite_conn, provenance
):
    validity = AuthorizationValidity(
        "auth-self-created",
        "policy-1",
        provenance.evolution_identity,
    )
    authorization = ExecutionAuthorization(
        request_provenance=provenance.provenance_id,
        owner_approved=True,
        evolution_identity=provenance.evolution_identity,
        approval_id=validity.authorization_id,
    )
    request = ExecutionCommitRequest(
        authorization,
        ExecutionIntentSnapshot.from_provenance(provenance),
        provenance.provenance_id,
        provenance.evolution_identity,
        provenance,
        validity,
    )

    with pytest.raises(PermissionError):
        require_trusted_execution(
            request,
            conn=sqlite_conn,
            actor="caller",
        )

    row = sqlite_conn.execute(
        "SELECT event_hash FROM audit_events WHERE event_id=?",
        ("execution-authorization:auth-self-created",),
    ).fetchone()
    assert row is None
