from gnosis.reflection.crypto import generate_keypair, sign, verify

def test_valid_signature_verifies():
    private_key, public_key = generate_keypair()
    payload = b"GNOZIS-AUTHORIZATION-V1|example"
    assert verify(public_key, payload, sign(private_key, payload)) is True

def test_payload_tampering_is_rejected():
    private_key, public_key = generate_keypair()
    signature = sign(private_key, b"original")
    assert verify(public_key, b"tampered", signature) is False

def test_signature_tampering_is_rejected():
    private_key, public_key = generate_keypair()
    payload = b"original"
    signature = sign(private_key, payload)
    altered = bytes([signature[0] ^ 1]) + signature[1:]
    assert verify(public_key, payload, altered) is False

def test_wrong_public_key_is_rejected():
    private_key, _ = generate_keypair()
    _, public_key = generate_keypair()
    payload = b"original"
    assert verify(public_key, payload, sign(private_key, payload)) is False

def test_malformed_signature_is_rejected():
    _, public_key = generate_keypair()
    assert verify(public_key, b"original", b"bad") is False
