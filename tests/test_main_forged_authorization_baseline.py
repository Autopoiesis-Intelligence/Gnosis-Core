"""Security regression on the exact main baseline.

A caller-constructed authorization must not be treated as trusted issuer proof.
This test is expected to fail until the trusted issuer boundary is implemented.
Do not weaken the assertion to match current behavior.
"""
from dataclasses import replace

import pytest

from gnosis.reflection.authority import (
    ExecutionAuthorization,
    ExecutionCommitRequest,
    ExecutionIntentSnapshot,
    _canonical_evolution_identity,
)
from gnosis.reflection.authorization_validity import AuthorizationValidity
from gnosis.reflection.trusted_execution_gate import require_trusted_execution


def test_main_rejects_caller_constructed_authorization_before_consumption(
    sqlite_conn, provenance
):
    # The fixture's evolution identity may be synthetic/non-canonical. Make the
    # request internally canonical so rejection cannot be explained by malformed
    # provenance instead of the missing trusted-issuer boundary.
    provenance = replace(
        provenance,
        evolution_identity=_canonical_evolution_identity(provenance),
    )
    authorization_id = "forged-main-baseline"
    authorization = ExecutionAuthorization(
        request_provenance=provenance.provenance_id,
        owner_approved=True,
        evolution_identity=provenance.evolution_identity,
        approval_id=authorization_id,
    )
    validity = AuthorizationValidity(
        authorization_id=authorization_id,
        policy_version="policy-1",
        validity_evidence_digest="evidence-1",
        revoked=False,
    )
    request = ExecutionCommitRequest(
        authorization=authorization,
        intent_snapshot=ExecutionIntentSnapshot.from_provenance(provenance),
        request_provenance=provenance.provenance_id,
        evolution_identity=provenance.evolution_identity,
        provenance=provenance,
        authorization_validity=validity,
    )

    with pytest.raises(PermissionError):
        require_trusted_execution(
            request,
            conn=sqlite_conn,
            actor="adversarial-main-baseline",
        )

    row = sqlite_conn.execute(
        "SELECT event_hash FROM audit_events WHERE event_id = ?",
        (f"execution-authorization:{authorization_id}",),
    ).fetchone()
    assert row is None, "rejected forged authorization must not be consumed"
