from datetime import datetime, timezone

import pytest

from gnosis.reflection.owner_authorization import authorization_id_for, canonical_payload, OwnerAuthorizationV1
from gnosis.reflection.owner_authorization_persistence import (
    consume_owner_authorization,
    load_owner_authorization,
    persist_owner_authorization,
)


FIELDS = {
    "issuer_id": "owner-issuer", "key_version": "key-v1", "authority_root": "root-1",
    "scope": "evolution.commit", "policy_version": "policy-v1", "request_provenance": "request-1",
    "evolution_identity": "evolution:abc", "parent_state_digest": "sha256:parent",
    "evidence_digest": "sha256:evidence", "authorization_id": "", "nonce": "nonce-persist-1",
    "valid_from": "2026-10-07T00:00:00Z", "valid_until": "2026-10-08T00:00:00Z",
}


def make_authorization(private_key):
    fields = {**FIELDS, "authorization_id": authorization_id_for(FIELDS)}
    return OwnerAuthorizationV1(**fields, signature=private_key.sign(canonical_payload(fields)))


def setup_db(conn):
    conn.executescript("""
    CREATE TABLE owner_authorizations (
        authorization_id TEXT PRIMARY KEY, nonce TEXT NOT NULL UNIQUE,
        issuer_id TEXT NOT NULL, key_version TEXT NOT NULL, authority_root TEXT NOT NULL,
        scope TEXT NOT NULL, policy_version TEXT NOT NULL, request_provenance TEXT NOT NULL,
        evolution_identity TEXT NOT NULL, parent_state_digest TEXT NOT NULL,
        evidence_digest TEXT NOT NULL, valid_from TEXT NOT NULL, valid_until TEXT NOT NULL,
        signature BLOB NOT NULL, consumed INTEGER NOT NULL DEFAULT 0,
        revoked INTEGER NOT NULL DEFAULT 0, integrity_digest TEXT NOT NULL
    );
    """)


def test_persist_load_and_consume_once():
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    conn = __import__("sqlite3").connect(":memory:")
    setup_db(conn)
    auth = make_authorization(Ed25519PrivateKey.generate())
    persist_owner_authorization(conn, auth)
    assert load_owner_authorization(conn, auth.authorization_id) == auth
    consume_owner_authorization(conn, auth)
    with pytest.raises(PermissionError, match="already consumed"):
        consume_owner_authorization(conn, auth)


def test_nonce_is_unique():
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    conn = __import__("sqlite3").connect(":memory:")
    setup_db(conn)
    first = make_authorization(Ed25519PrivateKey.generate())
    persist_owner_authorization(conn, first)
    fields = {**FIELDS, "authorization_id": "", "nonce": first.nonce}
    second = OwnerAuthorizationV1(**{**fields, "authorization_id": authorization_id_for(fields)}, signature=b"x")
    with pytest.raises(__import__("sqlite3").IntegrityError):
        persist_owner_authorization(conn, second)


def test_restart_preserves_consumed_state(tmp_path):
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    import sqlite3
    db = tmp_path / "auth.db"
    key = Ed25519PrivateKey.generate()
    auth = make_authorization(key)
    conn = sqlite3.connect(db)
    setup_db(conn)
    persist_owner_authorization(conn, auth)
    conn.commit()
    consume_owner_authorization(conn, auth)
    conn.commit()
    conn.close()
    reopened = sqlite3.connect(db)
    with pytest.raises(PermissionError, match="already consumed"):
        consume_owner_authorization(reopened, auth)


def test_tampered_persisted_record_fails_integrity_check():
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    import sqlite3
    conn = sqlite3.connect(":memory:")
    setup_db(conn)
    auth = make_authorization(Ed25519PrivateKey.generate())
    persist_owner_authorization(conn, auth)
    conn.execute("UPDATE owner_authorizations SET scope='tampered' WHERE authorization_id=?", (auth.authorization_id,))
    with pytest.raises(PermissionError, match="integrity"):
        consume_owner_authorization(conn, auth)


def test_concurrent_consume_allows_exactly_one_winner(tmp_path):
    import sqlite3
    import threading
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

    db = tmp_path / "concurrent.db"
    key = Ed25519PrivateKey.generate()
    auth = make_authorization(key)
    conn = sqlite3.connect(db)
    setup_db(conn)
    persist_owner_authorization(conn, auth)
    conn.commit()
    conn.close()

    barrier = threading.Barrier(2)
    outcomes = []
    lock = threading.Lock()

    def worker():
        local = sqlite3.connect(db, timeout=5.0)
        try:
            barrier.wait()
            local.execute("BEGIN IMMEDIATE")
            try:
                consume_owner_authorization(local, auth)
                local.commit()
                outcome = "accepted"
            except PermissionError:
                local.rollback()
                outcome = "rejected"
            with lock:
                outcomes.append(outcome)
        finally:
            local.close()

    threads = [threading.Thread(target=worker) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert sorted(outcomes) == ["accepted", "rejected"]
