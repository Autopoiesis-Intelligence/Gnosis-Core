"""Security regression on the exact current-main baseline.

A caller-constructed authorization must not be treated as trusted issuer proof.
This diagnostic intentionally fails while the trusted issuer boundary is absent.
It changes no production code, schema, migration, or runtime behavior.
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


def _forged_request(provenance, authorization_id):
    canonical_identity = _canonical_evolution_identity(provenance)
    provenance_for_gate = SimpleNamespace(
        **asdict(provenance),
        provenance_id=provenance.provenance_id,
        evolution_identity=canonical_identity,
    )
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
    return ExecutionCommitRequest(
        authorization=authorization,
        intent_snapshot=ExecutionIntentSnapshot.from_provenance(provenance_for_gate),
        request_provenance=provenance_for_gate.provenance_id,
        evolution_identity=canonical_identity,
        provenance=provenance_for_gate,
        authorization_validity=validity,
    )


def test_current_main_rejects_caller_constructed_authorization_before_consumption(
    sqlite_conn, provenance
):
    request = _forged_request(provenance, "seq113-forged-rejection")

    with pytest.raises(PermissionError):
        require_trusted_execution(
            request,
            conn=sqlite_conn,
            actor="seq113-forged-rejection",
        )

    row = sqlite_conn.execute(
        "SELECT event_hash FROM audit_events WHERE event_id = ?",
        ("execution-authorization:seq113-forged-rejection",),
    ).fetchone()
    assert row is None, "rejected forged authorization must not be consumed"


def test_current_main_does_not_consume_forged_authorization_even_if_gate_returns(
    sqlite_conn, provenance
):
    request = _forged_request(provenance, "seq113-forged-consumption")

    try:
        require_trusted_execution(
            request,
            conn=sqlite_conn,
            actor="seq113-forged-consumption",
        )
    except PermissionError:
        pass

    row = sqlite_conn.execute(
        "SELECT event_hash FROM audit_events WHERE event_id = ?",
        ("execution-authorization:seq113-forged-consumption",),
    ).fetchone()
    assert row is None, (
        "a forged authorization must never create a consumption audit event, "
        "including when the gate unexpectedly returns"
    )
