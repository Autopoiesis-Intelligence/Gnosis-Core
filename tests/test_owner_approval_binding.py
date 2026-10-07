from gnosis.reflection.authority import OwnerApproval
from gnosis.reflection.crypto import generate_keypair, sign_owner_authorization

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

def test_owner_approval_requires_valid_signature():
    private_key, public_key = generate_keypair()
    auth = authorization()
    approval = OwnerApproval.from_signed_authorization(
        auth,
        signature=sign_owner_authorization(private_key, auth),
        owner_public_key=public_key,
    )
    assert approval.approval_id == "a1"
    assert approval.evolution_identity == "ev1"

def test_owner_approval_rejects_tampered_authorization():
    private_key, public_key = generate_keypair()
    auth = authorization()
    signature = sign_owner_authorization(private_key, auth)
    auth["evolution_identity"] = "ev2"
    try:
        OwnerApproval.from_signed_authorization(
            auth, signature=signature, owner_public_key=public_key
        )
    except PermissionError:
        pass
    else:
        raise AssertionError("tampered authorization accepted")
