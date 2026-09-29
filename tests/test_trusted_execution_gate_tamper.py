import pytest
from dataclasses import FrozenInstanceError
from gnosis.evolution.provenance import build_provenance, canonical_digest
from gnosis.reflection.authorization_validity import AuthorizationValidity
from gnosis.reflection.authority import ExecutionAuthorization, ExecutionCommitRequest, ExecutionIntentSnapshot
from gnosis.reflection.trusted_execution_gate import require_trusted_execution
from gnosis.storage import connect


def _provenance():
    observations = {"result": "ok"}
    return build_provenance(
        candidate_id="c1",
        parent_state_id="s1",
        parent_state_digest="pd",
        proposed_state_digest=canonical_digest({"state": "new"}),
        observations=observations,
        evidence_digest=canonical_digest(observations),
        proposed_state_content_id="content-1",
        candidate_binding_digest="binding-1",
        evaluation_status="PASS",
        shadow_status="UNCHANGED",
        invariant_status="PRESERVED",
        governance_decision="ALLOW",
    )


def _request(provenance, authorization_id="auth-direct", policy="policy-1", evidence="ev-1"):
    validity = AuthorizationValidity(authorization_id, policy, evidence)
    authorization = ExecutionAuthorization(
        request_provenance=provenance.provenance_id,
        owner_approved=True,
        evolution_identity=provenance.evolution_identity,
        approval_id=authorization_id,
    )
    return ExecutionCommitRequest(
        authorization,
        ExecutionIntentSnapshot.from_provenance(provenance),
        provenance.provenance_id,
        provenance.evolution_identity,
        provenance,
        validity,
    )


def test_validity_is_immutable():
    v = AuthorizationValidity("auth-t", "policy-1", "ev-1")
    with pytest.raises(FrozenInstanceError):
        v.authorization_id = "forged"


def test_unissued_execution_authorization_is_rejected_before_consumption():
    conn = connect()
    try:
        request = _request(_provenance())
        with pytest.raises(PermissionError):
            require_trusted_execution(request, conn=conn, actor="trusted-owner")
        row = conn.execute(
            "SELECT event_hash FROM audit_events WHERE event_id=?",
            ("execution-authorization:auth-direct",),
        ).fetchone()
        assert row is None
    finally:
        conn.close()


def test_unissued_authorization_cannot_use_caller_controlled_validity():
    conn = connect()
    try:
        request = _request(
            _provenance(),
            authorization_id="auth-substitution",
            policy="policy-forged",
            evidence="evidence-forged",
        )
        with pytest.raises(PermissionError):
            require_trusted_execution(request, conn=conn, actor="trusted-owner")
        row = conn.execute(
            "SELECT event_hash FROM audit_events WHERE event_id=?",
            ("execution-authorization:auth-substitution",),
        ).fetchone()
        assert row is None
    finally:
        conn.close()
