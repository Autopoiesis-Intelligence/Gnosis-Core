"""SEQ 124 regression: no caller-constructed authorization may be consumed."""
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


def test_valid_looking_caller_constructed_authorization_is_blocked_before_consumption(
    sqlite_conn, provenance
):
    request = _forged_request(provenance, "seq124-forged-rejection")

    with pytest.raises(PermissionError, match="verifier is not configured"):
        require_trusted_execution(
            request,
            conn=sqlite_conn,
            actor="seq124-forged-rejection",
        )

    row = sqlite_conn.execute(
        "SELECT event_hash FROM audit_events WHERE event_id = ?",
        ("execution-authorization:seq124-forged-rejection",),
    ).fetchone()
    assert row is None, "rejected authorization must not create a consumption event"


def test_blocked_authorization_does_not_mutate_audit_events(sqlite_conn, provenance):
    request = _forged_request(provenance, "seq124-forged-audit-invariance")
    before = sqlite_conn.execute(
        "SELECT event_id, event_hash FROM audit_events ORDER BY event_id"
    ).fetchall()

    with pytest.raises(PermissionError):
        require_trusted_execution(
            request,
            conn=sqlite_conn,
            actor="seq124-forged-audit-invariance",
        )

    after = sqlite_conn.execute(
        "SELECT event_id, event_hash FROM audit_events ORDER BY event_id"
    ).fetchall()
    assert after == before
