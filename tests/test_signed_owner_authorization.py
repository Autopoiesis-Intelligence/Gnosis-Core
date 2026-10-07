from gnosis.reflection.crypto import generate_keypair, sign_owner_authorization, verify_owner_authorization

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

def test_valid_owner_signature_verifies():
    private_key, public_key = generate_keypair()
    auth = authorization()
    signature = sign_owner_authorization(private_key, auth)
    assert verify_owner_authorization(public_key, auth, signature) is True

def test_evolution_identity_tampering_is_rejected():
    private_key, public_key = generate_keypair()
    auth = authorization()
    signature = sign_owner_authorization(private_key, auth)
    auth["evolution_identity"] = "ev2"
    assert verify_owner_authorization(public_key, auth, signature) is False

def test_policy_tampering_is_rejected():
    private_key, public_key = generate_keypair()
    auth = authorization()
    signature = sign_owner_authorization(private_key, auth)
    auth["policy_version"] = "p2"
    assert verify_owner_authorization(public_key, auth, signature) is False

def test_wrong_owner_key_is_rejected():
    private_key, _ = generate_keypair()
    _, wrong_public_key = generate_keypair()
    auth = authorization()
    signature = sign_owner_authorization(private_key, auth)
    assert verify_owner_authorization(wrong_public_key, auth, signature) is False

def test_signature_tampering_is_rejected():
    private_key, public_key = generate_keypair()
    auth = authorization()
    signature = sign_owner_authorization(private_key, auth)
    signature = bytes([signature[0] ^ 1]) + signature[1:]
    assert verify_owner_authorization(public_key, auth, signature) is False
