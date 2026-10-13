from gnosis.reflection.authority import OwnerApproval
from gnosis.reflection.crypto import generate_keypair, sign_owner_authorization
from gnosis.reflection.trusted_issuer import TrustedIssuerInput, TrustedOwnerIssuer

def authorization():
    return {
        "authority_root": "owner-root",
        "scope": "bounded",
        "policy_version": "p1",
        "evidence_digest": "e1",
        "request_provenance": "r1",
        "evolution_identity": "ev1",
        "approval_id": "a1",
    }

def approval():
    private_key, public_key = generate_keypair()
    auth = authorization()
    return OwnerApproval.from_signed_authorization(
        auth,
        signature=sign_owner_authorization(private_key, auth),
        owner_public_key=public_key,
    )

def test_issuer_accepts_verified_matching_bindings():
    a = approval()
    issuer = TrustedOwnerIssuer("owner-root", "bounded", "p1")
    result = issuer.issue(
        TrustedIssuerInput(a, "owner-root", "bounded", "p1", "e1"),
        request_provenance="r1",
        evolution_identity="ev1",
    )
    assert result.owner_approved is True

def test_issuer_rejects_approval_root_mismatch():
    a = approval()
    issuer = TrustedOwnerIssuer("other-root", "bounded", "p1")
    try:
        issuer.issue(TrustedIssuerInput(a, "owner-root", "bounded", "p1", "e1"), request_provenance="r1", evolution_identity="ev1")
    except PermissionError:
        pass
    else:
        raise AssertionError("root mismatch accepted")

def test_issuer_rejects_approval_policy_mismatch():
    a = approval()
    issuer = TrustedOwnerIssuer("owner-root", "other-scope", "p1")
    try:
        issuer.issue(TrustedIssuerInput(a, "owner-root", "bounded", "p1", "e1"), request_provenance="r1", evolution_identity="ev1")
    except PermissionError:
        pass
    else:
        raise AssertionError("scope mismatch accepted")
