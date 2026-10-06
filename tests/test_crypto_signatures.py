from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from gnosis.crypto import Ed25519SignatureVerifier


def test_ed25519_valid_signature_verifies() -> None:
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key().public_bytes_raw()
    message = b"GNOZIS/OWNER-AUTHORIZATION/v1\x00payload"
    signature = private_key.sign(message)

    assert Ed25519SignatureVerifier().verify(
        public_key=public_key, message=message, signature=signature
    )


def test_ed25519_changed_message_is_rejected() -> None:
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key().public_bytes_raw()
    signature = private_key.sign(b"original")

    assert not Ed25519SignatureVerifier().verify(
        public_key=public_key, message=b"changed", signature=signature
    )


def test_ed25519_wrong_key_is_rejected() -> None:
    signer = Ed25519PrivateKey.generate()
    wrong_key = Ed25519PrivateKey.generate().public_key().public_bytes_raw()
    message = b"owner-approval"
    signature = signer.sign(message)

    assert not Ed25519SignatureVerifier().verify(
        public_key=wrong_key, message=message, signature=signature
    )


def test_ed25519_modified_signature_is_rejected() -> None:
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key().public_bytes_raw()
    message = b"owner-approval"
    signature = bytearray(private_key.sign(message))
    signature[-1] ^= 1

    assert not Ed25519SignatureVerifier().verify(
        public_key=public_key, message=message, signature=bytes(signature)
    )


def test_ed25519_malformed_public_key_fails_closed() -> None:
    assert not Ed25519SignatureVerifier().verify(
        public_key=b"too-short", message=b"owner-approval", signature=b"invalid"
    )


def test_ed25519_malformed_signature_fails_closed() -> None:
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key().public_bytes_raw()

    assert not Ed25519SignatureVerifier().verify(
        public_key=public_key, message=b"owner-approval", signature=b"too-short"
    )


def test_ed25519_rejects_implicit_text_encoding() -> None:
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key().public_bytes_raw()
    message = b"owner-approval"
    signature = private_key.sign(message)

    assert not Ed25519SignatureVerifier().verify(
        public_key=public_key, message=message.decode(), signature=signature
    )
