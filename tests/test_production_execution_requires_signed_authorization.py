"""Security regression tests for the signed owner-authorization commit boundary."""
import base64

import pytest
from nacl.signing import SigningKey

from gnosis.reflection.execution_adapter import SQLiteExecutionCommitAdapter
from gnosis.reflection.owner_authorization import (
    DOMAIN,
    ProductionAuthorization,
    TrustedIssuerKey,
    canonical_authorization_bytes,
    verify_production_authorization,
)
from gnosis.reflection.trusted_execution_gate import require_trusted_execution


class StaticKeyResolver:
    def __init__(self, key):
        self.key = key

    def resolve(self, issuer_id, key_version):
        if (issuer_id, key_version) == (self.key.issuer_id, self.key.key_version):
            return self.key
        return None


def signed_authorization(signing_key):
    unsigned = ProductionAuthorization(
        authorization_id="", issuer_id="owner-issuer", key_version="v1",
        authority_scope=("evolution.commit",), policy_version="policy-v1",
        evolution_identity="evolution-1", parent_state_digest="parent-digest",
        request_provenance="request-1", valid_from=10, expires_at=200,
        nonce="nonce-1", proposal_binding_digest="sha256:proposal-binding-test", signature="",
    )
    authorization_id = unsigned.expected_authorization_id()
    to_sign = ProductionAuthorization(
        authorization_id=authorization_id, issuer_id=unsigned.issuer_id,
        key_version=unsigned.key_version, authority_scope=unsigned.authority_scope,
        policy_version=unsigned.policy_version, evolution_identity=unsigned.evolution_identity,
        parent_state_digest=unsigned.parent_state_digest,
        request_provenance=unsigned.request_provenance, valid_from=unsigned.valid_from,
        expires_at=unsigned.expires_at, nonce=unsigned.nonce,
        proposal_binding_digest=unsigned.proposal_binding_digest, signature="",
    )
    signature = base64.b64encode(signing_key.sign(to_sign.canonical_bytes()).signature).decode("ascii")
    return ProductionAuthorization(
        authorization_id=to_sign.authorization_id, issuer_id=to_sign.issuer_id,
        key_version=to_sign.key_version, authority_scope=to_sign.authority_scope,
        policy_version=to_sign.policy_version, evolution_identity=to_sign.evolution_identity,
        parent_state_digest=to_sign.parent_state_digest,
        request_provenance=to_sign.request_provenance, valid_from=to_sign.valid_from,
        expires_at=to_sign.expires_at, nonce=to_sign.nonce,
        proposal_binding_digest=to_sign.proposal_binding_digest, signature=signature,
    )


def test_commit_rejects_missing_signed_authorization_before_touching_storage():
    with pytest.raises(PermissionError, match="signed production owner authorization is required"):
        SQLiteExecutionCommitAdapter().commit(None, None, None, None, None, actor="test")


@pytest.mark.parametrize(
    ("policy", "digest", "message"),
    [
        ("", "digest", "trusted expected policy version is required"),
        ("policy-v1", "", "trusted expected validity evidence digest is required"),
    ],
)
def test_gate_rejects_missing_independent_trust_anchors(policy, digest, message):
    with pytest.raises(PermissionError, match=message):
        require_trusted_execution(
            None, conn=None, actor="test",
            expected_policy_version=policy,
            expected_evidence_digest=digest,
        )


def test_ed25519_verifier_accepts_valid_signature_and_exact_bindings():
    signing_key = SigningKey.generate()
    authorization = signed_authorization(signing_key)
    key = TrustedIssuerKey("owner-issuer", "v1", bytes(signing_key.verify_key))
    resolved = verify_production_authorization(
        authorization, StaticKeyResolver(key), now=100,
        expected_scope={"evolution.commit"}, expected_policy_version="policy-v1",
        expected_evolution_identity="evolution-1",
        expected_parent_state_digest="parent-digest",
        expected_request_provenance="request-1",
        expected_proposal_binding_digest="sha256:proposal-binding-test",
    )
    assert resolved == key


def test_ed25519_verifier_rejects_modified_signature():
    signing_key = SigningKey.generate()
    authorization = signed_authorization(signing_key)
    tampered = ProductionAuthorization(
        **{**authorization.__dict__, "signature": base64.b64encode(b"x" * 64).decode("ascii")}
    )
    key = TrustedIssuerKey("owner-issuer", "v1", bytes(signing_key.verify_key))
    with pytest.raises(PermissionError, match="signature verification failed"):
        verify_production_authorization(
            tampered, StaticKeyResolver(key), now=100,
            expected_scope={"evolution.commit"}, expected_policy_version="policy-v1",
            expected_evolution_identity="evolution-1",
            expected_parent_state_digest="parent-digest",
            expected_request_provenance="request-1",
            expected_proposal_binding_digest="sha256:proposal-binding-test",
        )


def test_ed25519_verifier_rejects_proposal_binding_for_different_proposal():
    signing_key = SigningKey.generate()
    authorization = signed_authorization(signing_key)
    key = TrustedIssuerKey("owner-issuer", "v1", bytes(signing_key.verify_key))
    with pytest.raises(PermissionError, match="proposal-binding mismatch"):
        verify_production_authorization(
            authorization, StaticKeyResolver(key), now=100,
            expected_scope={"evolution.commit"}, expected_policy_version="policy-v1",
            expected_evolution_identity="evolution-1",
            expected_parent_state_digest="parent-digest",
            expected_request_provenance="request-1",
            expected_proposal_binding_digest="sha256:another-proposal-binding",
        )


def test_authorization_protocol_uses_canonical_gnosis_core_domain():
    assert DOMAIN == "gnosis-core:owner-authorization:v1"
