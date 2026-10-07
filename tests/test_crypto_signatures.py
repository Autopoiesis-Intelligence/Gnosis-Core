from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from gnosis.crypto import Ed25519SignatureVerifier


def test_valid_signature_verifies() -> None:
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key().public_bytes_raw()
    message = b"owner-approval"
    assert Ed25519SignatureVerifier().verify(public_key=public_key, message=message, signature=private_key.sign(message))


def test_changed_message_is_rejected() -> None:
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key().public_bytes_raw()
    signature = private_key.sign(b"original")
    assert not Ed25519SignatureVerifier().verify(public_key=public_key, message=b"changed", signature=signature)


def test_wrong_key_is_rejected() -> None:
    signer = Ed25519PrivateKey.generate()
    wrong_key = Ed25519PrivateKey.generate().public_key().public_bytes_raw()
    assert not Ed25519SignatureVerifier().verify(public_key=wrong_key, message=b"owner-approval", signature=signer.sign(b"owner-approval"))


def test_modified_signature_is_rejected() -> None:
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key().public_bytes_raw()
    signature = bytearray(private_key.sign(b"owner-approval"))
    signature[-1] ^= 1
    assert not Ed25519SignatureVerifier().verify(public_key=public_key, message=b"owner-approval", signature=bytes(signature))


def test_malformed_public_key_fails_closed() -> None:
    assert not Ed25519SignatureVerifier().verify(public_key=b"short", message=b"owner-approval", signature=b"invalid")


def test_malformed_signature_fails_closed() -> None:
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key().public_bytes_raw()
    assert not Ed25519SignatureVerifier().verify(public_key=public_key, message=b"owner-approval", signature=b"short")


def test_text_message_is_rejected() -> None:
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key().public_bytes_raw()
    assert not Ed25519SignatureVerifier().verify(public_key=public_key, message="owner-approval", signature=private_key.sign(b"owner-approval"))
