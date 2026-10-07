from gnosis.reflection.owner_trust import OwnerTrustAnchor


VALID_KEY_HEX = "000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f"


def test_owner_trust_anchor_loads_from_environment(monkeypatch) -> None:
    monkeypatch.setenv("GNOZIS_OWNER_ID", "owner-1")
    monkeypatch.setenv("GNOZIS_OWNER_KEY_ID", "key-1")
    monkeypatch.setenv("GNOZIS_OWNER_TRUSTED_ED25519_PUBLIC_KEY_HEX", VALID_KEY_HEX)

    anchor = OwnerTrustAnchor.from_environment()

    assert anchor is not None
    assert anchor.owner_id == "owner-1"
    assert anchor.key_id == "key-1"
    assert anchor.public_key == bytes.fromhex(VALID_KEY_HEX)


def test_missing_owner_trust_anchor_fails_closed(monkeypatch) -> None:
    monkeypatch.delenv("GNOZIS_OWNER_ID", raising=False)
    monkeypatch.delenv("GNOZIS_OWNER_KEY_ID", raising=False)
    monkeypatch.delenv("GNOZIS_OWNER_TRUSTED_ED25519_PUBLIC_KEY_HEX", raising=False)

    assert OwnerTrustAnchor.from_environment() is None


def test_malformed_public_key_fails_closed(monkeypatch) -> None:
    monkeypatch.setenv("GNOZIS_OWNER_ID", "owner-1")
    monkeypatch.setenv("GNOZIS_OWNER_KEY_ID", "key-1")
    monkeypatch.setenv("GNOZIS_OWNER_TRUSTED_ED25519_PUBLIC_KEY_HEX", "not-hex")

    assert OwnerTrustAnchor.from_environment() is None


def test_wrong_public_key_length_fails_closed(monkeypatch) -> None:
    monkeypatch.setenv("GNOZIS_OWNER_ID", "owner-1")
    monkeypatch.setenv("GNOZIS_OWNER_KEY_ID", "key-1")
    monkeypatch.setenv("GNOZIS_OWNER_TRUSTED_ED25519_PUBLIC_KEY_HEX", "00")

    assert OwnerTrustAnchor.from_environment() is None


def test_owner_and_key_identity_must_match() -> None:
    anchor = OwnerTrustAnchor("owner-1", "key-1", bytes(32))

    assert anchor.matches(owner_id="owner-1", key_id="key-1")
    assert not anchor.matches(owner_id="owner-2", key_id="key-1")
    assert not anchor.matches(owner_id="owner-1", key_id="key-2")
