"""Security regression on the exact main baseline.

A caller-constructed authorization must not be treated as trusted issuer proof.
This test is expected to fail until the trusted issuer boundary is implemented.
Do not weaken the assertion to match current behavior.
"""
from dataclasses import asdict
from types import SimpleNamespace

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
    # Isolate the missing issuer-authentication boundary from the current
    # mismatch between EvidenceProvenance.evolution_identity and the gate's
    # independently recomputed canonical identity.
    canonical_identity = _canonical_evolution_identity(provenance)
    provenance_for_gate = SimpleNamespace(
        **asdict(provenance),
        provenance_id=provenance.provenance_id,
        evolution_identity=canonical_identity,
    )
    authorization_id = "forged-main-baseline"
    authorization = ExecutionAuthorization(
        request_provenance=provenance_for_gate.provenance_id,
        owner_approved=True,
        evolution_identity=canonical_identity,
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
        intent_snapshot=ExecutionIntentSnapshot.from_provenance(provenance_for_gate),
        request_provenance=provenance_for_gate.provenance_id,
        evolution_identity=canonical_identity,
        provenance=provenance_for_gate,
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



def test_main_does_not_consume_forged_authorization_even_if_gate_returns(
    sqlite_conn, provenance
):
    """Independent diagnostic: inspect consumption even when the gate fails open."""
    canonical_identity = _canonical_evolution_identity(provenance)
    provenance_for_gate = SimpleNamespace(
        **asdict(provenance),
        provenance_id=provenance.provenance_id,
        evolution_identity=canonical_identity,
    )
    authorization_id = "forged-main-consumption-diagnostic"
    authorization = ExecutionAuthorization(
        request_provenance=provenance_for_gate.provenance_id,
        owner_approved=True,
        evolution_identity=canonical_identity,
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
        intent_snapshot=ExecutionIntentSnapshot.from_provenance(provenance_for_gate),
        request_provenance=provenance_for_gate.provenance_id,
        evolution_identity=canonical_identity,
        provenance=provenance_for_gate,
        authorization_validity=validity,
    )

    try:
        require_trusted_execution(
            request,
            conn=sqlite_conn,
            actor="adversarial-main-consumption-diagnostic",
        )
    except PermissionError:
        pass

    row = sqlite_conn.execute(
        "SELECT event_hash FROM audit_events WHERE event_id = ?",
        (f"execution-authorization:{authorization_id}",),
    ).fetchone()
    assert row is None, (
        "a forged authorization must never create a consumption audit event, "
        "including when the gate unexpectedly returns"
    )
