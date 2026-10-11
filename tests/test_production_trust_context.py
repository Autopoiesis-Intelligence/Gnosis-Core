"""Focused tests for production trust-context binding of signed grants."""
from __future__ import annotations

import base64
from dataclasses import replace
from types import SimpleNamespace

import pytest
from nacl.signing import SigningKey

from gnosis.reflection.authority import ExecutionAuthorization
from gnosis.reflection.authorization_validity import AuthorizationValidity
from gnosis.reflection.owner_authorization import (
    ACTIVE,
    ProductionAuthorization,
    TrustedIssuerKey,
)
from gnosis.reflection.production_trust_context import ProductionTrustContext
from gnosis.reflection.authorization_consumption import consume_authorization_nonce_in_transaction
from gnosis.storage.database import transaction


ISSUER = "owner-root"
KEY_VERSION = "key-1"
SCOPE = frozenset({"core:commit"})
POLICY = "policy-1"
EVOLUTION = "evolution:abc"
PARENT = "state:parent"
PROVENANCE = "request:abc"
NOW = 1_800_000_000


class Resolver:
    def __init__(self, key: TrustedIssuerKey | None):
        self.key = key

    def resolve(self, issuer_id: str, key_version: str) -> TrustedIssuerKey | None:
        if self.key is None:
            return None
        if (issuer_id, key_version) != (self.key.issuer_id, self.key.key_version):
            return None
        return self.key


def signed_authorization(signing_key: SigningKey) -> ProductionAuthorization:
    unsigned = ProductionAuthorization(
        authorization_id="pending",
        issuer_id=ISSUER,
        key_version=KEY_VERSION,
        authority_scope=("core:commit",),
        policy_version=POLICY,
        evolution_identity=EVOLUTION,
        parent_state_digest=PARENT,
        request_provenance=PROVENANCE,
        valid_from=NOW - 60,
        expires_at=NOW + 60,
        nonce="nonce-1",
        signature="pending",
    )
    unsigned = replace(unsigned, authorization_id=unsigned.expected_authorization_id())
    signature = signing_key.sign(unsigned.canonical_bytes()).signature
    return replace(unsigned, signature=base64.b64encode(signature).decode("ascii"))


def make_request(authorization: ProductionAuthorization, *, evolution: str = EVOLUTION):
    validity = AuthorizationValidity(
        authorization_id=authorization.authorization_id,
        policy_version=POLICY,
        validity_evidence_digest="legacy-evidence",
    )
    legacy_authorization = ExecutionAuthorization(
        request_provenance=PROVENANCE,
        owner_approved=True,
        evolution_identity=evolution,
        approval_id=authorization.authorization_id,
    )
    provenance = SimpleNamespace(
        parent_state_digest=PARENT,
    )
    return SimpleNamespace(
        authorization=legacy_authorization,
        authorization_validity=validity,
        evolution_identity=evolution,
        request_provenance=PROVENANCE,
        provenance=provenance,
    )


def make_context(signing_key: SigningKey, *, policy: str = POLICY, clock= lambda: NOW):
    key = TrustedIssuerKey(
        issuer_id=ISSUER,
        key_version=KEY_VERSION,
        public_key=bytes(signing_key.verify_key),
        status=ACTIVE,
        valid_from=NOW - 100,
        expires_at=NOW + 100,
    )
    return ProductionTrustContext(
        issuer_key_resolver=Resolver(key),
        authority_scope=SCOPE,
        policy_version=policy,
        trusted_clock=clock,
    )


def test_signed_grant_is_verified_against_commit_request():
    signing_key = SigningKey.generate()
    authorization = signed_authorization(signing_key)

    key = make_context(signing_key).verify_commit(authorization, make_request(authorization))

    assert key.issuer_id == ISSUER
    assert key.key_version == KEY_VERSION


def test_missing_trust_context_inputs_are_rejected():
    signing_key = SigningKey.generate()
    authorization = signed_authorization(signing_key)

    context = make_context(signing_key, policy="policy-2")
    with pytest.raises(PermissionError, match="validity policy"):
        context.verify_commit(authorization, make_request(authorization))


def test_signed_grant_evolution_mismatch_is_rejected():
    signing_key = SigningKey.generate()
    authorization = signed_authorization(signing_key)

    with pytest.raises(PermissionError, match="evolution mismatch"):
        make_context(signing_key).verify_commit(
            authorization,
            make_request(authorization, evolution="evolution:forged"),
        )


def test_signed_grant_with_tampered_signature_is_rejected():
    signing_key = SigningKey.generate()
    authorization = signed_authorization(signing_key)
    tampered = replace(
        authorization,
        signature=base64.b64encode(b"x" * 64).decode("ascii"),
    )

    with pytest.raises(PermissionError, match="signature verification failed"):
        make_context(signing_key).verify_commit(tampered, make_request(tampered))


def test_trusted_clock_is_required_to_return_integer_timestamp():
    signing_key = SigningKey.generate()
    authorization = signed_authorization(signing_key)

    context = make_context(signing_key, clock=lambda: "not-a-timestamp")
    with pytest.raises(PermissionError, match="trusted clock"):
        context.verify_commit(authorization, make_request(authorization))



def test_authorization_nonce_is_consumed_once_inside_transaction(sqlite_conn):
    with transaction(sqlite_conn):
        consume_authorization_nonce_in_transaction(
            sqlite_conn,
            "nonce-once",
            authorization_id="auth:once",
            actor="trusted-owner",
        )

    row = sqlite_conn.execute(
        "SELECT event_hash FROM audit_events WHERE event_id=?",
        ("execution-authorization-nonce:nonce-once",),
    ).fetchone()
    assert row is not None

    with pytest.raises(PermissionError, match="nonce already consumed"):
        with transaction(sqlite_conn):
            consume_authorization_nonce_in_transaction(
                sqlite_conn,
                "nonce-once",
                authorization_id="auth:second",
                actor="trusted-owner",
            )


def _make_real_commit_case(sqlite_conn, *, nonce: str = "integration-nonce"):
    from gnosis.core import Candidate, State
    from gnosis.evolution.provenance import build_provenance, canonical_digest
    from gnosis.instances.instance import Instance
    from gnosis.storage import save_instance
    from gnosis.reflection.authority import ExecutionCommitRequest, ExecutionIntentSnapshot
    from gnosis.reflection.execution_adapter import SQLiteExecutionCommitAdapter

    signing_key = SigningKey.generate()
    instance = Instance.create_root("integration-owner", State(elements={"before": 1}))
    save_instance(sqlite_conn, instance)
    parent_state_id = instance.engine.state.state_id
    proposed = instance.engine.state.with_elements({"after": 2})
    candidate = Candidate(parent_state_id, proposed, "authorized-integration")
    record = instance.engine.step(candidate)
    observations = {"integration": "authorized"}
    provenance = build_provenance(
        candidate_id=candidate.candidate_id,
        parent_state_id=parent_state_id,
        parent_state_digest=parent_state_id,
        proposed_state_digest=proposed.state_id,
        observations=observations,
        proposed_state_content_id=proposed.content_id,
        candidate_binding_digest=candidate.binding_digest(parent_state_id),
        evidence_digest=canonical_digest(observations),
        evaluation_status="PASS",
        shadow_status="UNCHANGED",
        invariant_status="PRESERVED",
        governance_decision="ALLOW",
    )
    unsigned = ProductionAuthorization(
        authorization_id="pending",
        issuer_id=ISSUER,
        key_version=KEY_VERSION,
        authority_scope=("core:commit",),
        policy_version=POLICY,
        evolution_identity=provenance.evolution_identity,
        parent_state_digest=parent_state_id,
        request_provenance=provenance.provenance_id,
        valid_from=NOW - 60,
        expires_at=NOW + 60,
        nonce=nonce,
        signature="pending",
    )
    unsigned = replace(unsigned, authorization_id=unsigned.expected_authorization_id())
    signed = replace(
        unsigned,
        signature=base64.b64encode(signing_key.sign(unsigned.canonical_bytes()).signature).decode("ascii"),
    )
    request = ExecutionCommitRequest(
        authorization=ExecutionAuthorization(
            request_provenance=provenance.provenance_id,
            owner_approved=True,
            evolution_identity=provenance.evolution_identity,
            approval_id=signed.authorization_id,
        ),
        intent_snapshot=ExecutionIntentSnapshot.from_provenance(provenance),
        request_provenance=provenance.provenance_id,
        evolution_identity=provenance.evolution_identity,
        provenance=provenance,
        authorization_validity=AuthorizationValidity(
            authorization_id=signed.authorization_id,
            policy_version=POLICY,
            validity_evidence_digest="legacy-evidence",
        ),
    )
    return (
        SQLiteExecutionCommitAdapter(), instance, candidate, record, request,
        signed, make_context(signing_key), proposed,
    )


def test_real_authorized_commit_persists_state_and_rejects_replay(sqlite_conn):
    from gnosis.storage import load_instance

    adapter, instance, candidate, record, request, signed, context, proposed = _make_real_commit_case(sqlite_conn)
    result = adapter.commit(
        sqlite_conn, instance, candidate, record, request,
        actor="integration-owner",
        production_authorization=signed,
        trust_context=context,
    )
    assert result.resulting_state_id == proposed.state_id
    assert load_instance(sqlite_conn, instance.instance_id).engine.state.state_id == proposed.state_id
    assert sqlite_conn.execute(
        "SELECT 1 FROM audit_events WHERE event_id=?",
        (f"execution-authorization-nonce:{signed.nonce}",),
    ).fetchone() is not None

    with pytest.raises(PermissionError, match="nonce already consumed|already consumed"):
        adapter.commit(
            sqlite_conn, instance, candidate, record, request,
            actor="integration-owner",
            production_authorization=signed,
            trust_context=context,
        )


def test_real_authorized_commit_rolls_back_nonce_when_persistence_fails(sqlite_conn):
    adapter, instance, candidate, record, request, signed, context, _ = _make_real_commit_case(
        sqlite_conn, nonce="rollback-integration-nonce"
    )
    request.failure_injection = "after_audit"
    with pytest.raises(RuntimeError, match="after_audit"):
        adapter.commit(
            sqlite_conn, instance, candidate, record, request,
            actor="integration-owner",
            production_authorization=signed,
            trust_context=context,
        )
    assert sqlite_conn.execute(
        "SELECT 1 FROM audit_events WHERE event_id=?",
        (f"execution-authorization-nonce:{signed.nonce}",),
    ).fetchone() is None
    assert sqlite_conn.execute(
        "SELECT 1 FROM transitions WHERE transition_id=?",
        (record.transition_id,),
    ).fetchone() is None
    assert instance.engine.state.state_id != record.to_state_id
