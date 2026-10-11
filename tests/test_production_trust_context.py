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
