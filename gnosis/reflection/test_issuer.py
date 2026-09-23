"""Explicitly non-production test authority for E5.20.

This module is a development/test vertical slice only. It must never be used
as a production owner-authority implementation or with real external secrets.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import hmac
import json
import sqlite3
import secrets

from gnosis.evolution.provenance import canonical_digest


TEST_ISSUER_ID = "test-authority"
TEST_ISSUER_VERSION = "v1"
_DOMAIN = "gnozis:test-authorization:v1"


@dataclass(frozen=True)
class TestAuthorization:
    authorization_id: str
    issuer_id: str
    issuer_version: str
    request_provenance: str
    evolution_identity: str
    parent_state_digest: str
    policy_version: str
    nonce: str
    expires_at: int
    scope: tuple[str, ...]
    signature: str

    def payload(self) -> dict[str, object]:
        return {
            "domain": _DOMAIN,
            "issuer_id": self.issuer_id,
            "issuer_version": self.issuer_version,
            "request_provenance": self.request_provenance,
            "evolution_identity": self.evolution_identity,
            "parent_state_digest": self.parent_state_digest,
            "policy_version": self.policy_version,
            "nonce": self.nonce,
            "expires_at": self.expires_at,
            "scope": list(self.scope),
        }


def _canonical_payload(payload: dict[str, object]) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def _sign(secret: bytes, payload: dict[str, object]) -> str:
    return hmac.new(secret, _canonical_payload(payload), hashlib.sha256).hexdigest()


class TestAuthorizationIssuer:
    """Ephemeral test issuer; intentionally not a production trust root."""

    def __init__(self, secret: bytes | None = None) -> None:
        self._secret = secret or secrets.token_bytes(32)

    def issue(
        self,
        *,
        request_provenance: str,
        evolution_identity: str,
        parent_state_digest: str,
        policy_version: str,
        scope: tuple[str, ...],
        expires_at: int,
    ) -> TestAuthorization:
        if not all((request_provenance, evolution_identity, parent_state_digest, policy_version)):
            raise ValueError("test authorization requires exact binding fields")
        if expires_at <= 0:
            raise ValueError("expires_at must be positive")
        nonce = secrets.token_hex(16)
        unsigned = TestAuthorization(
            authorization_id="",
            issuer_id=TEST_ISSUER_ID,
            issuer_version=TEST_ISSUER_VERSION,
            request_provenance=request_provenance,
            evolution_identity=evolution_identity,
            parent_state_digest=parent_state_digest,
            policy_version=policy_version,
            nonce=nonce,
            expires_at=expires_at,
            scope=tuple(sorted(set(scope))),
            signature="",
        )
        payload = unsigned.payload()
        authorization_id = "auth:" + canonical_digest(payload)[:32]
        signature = _sign(self._secret, payload)
        return TestAuthorization(
            authorization_id=authorization_id,
            signature=signature,
            **{k: getattr(unsigned, k) for k in (
                "issuer_id", "issuer_version", "request_provenance",
                "evolution_identity", "parent_state_digest", "policy_version",
                "nonce", "expires_at", "scope"
            )},
        )

    def verify(self, authorization: TestAuthorization) -> bool:
        if authorization.issuer_id != TEST_ISSUER_ID or authorization.issuer_version != TEST_ISSUER_VERSION:
            return False
        expected_id = "auth:" + canonical_digest(authorization.payload())[:32]
        if authorization.authorization_id != expected_id:
            return False
        return hmac.compare_digest(authorization.signature, _sign(self._secret, authorization.payload()))


def initialize_test_authorization_store(conn: sqlite3.Connection) -> None:
    conn.execute(
        """CREATE TABLE IF NOT EXISTS test_authorizations (
            authorization_id TEXT PRIMARY KEY,
            issuer_id TEXT NOT NULL,
            issuer_version TEXT NOT NULL,
            request_provenance TEXT NOT NULL,
            evolution_identity TEXT NOT NULL,
            parent_state_digest TEXT NOT NULL,
            policy_version TEXT NOT NULL,
            nonce TEXT NOT NULL UNIQUE,
            expires_at INTEGER NOT NULL,
            scope_json TEXT NOT NULL,
            signature TEXT NOT NULL,
            consumed INTEGER NOT NULL DEFAULT 0,
            revoked INTEGER NOT NULL DEFAULT 0
        )"""
    )
    conn.commit()


def persist_test_authorization(conn: sqlite3.Connection, authorization: TestAuthorization) -> None:
    conn.execute(
        """INSERT INTO test_authorizations
        (authorization_id, issuer_id, issuer_version, request_provenance,
         evolution_identity, parent_state_digest, policy_version, nonce,
         expires_at, scope_json, signature)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            authorization.authorization_id, authorization.issuer_id,
            authorization.issuer_version, authorization.request_provenance,
            authorization.evolution_identity, authorization.parent_state_digest,
            authorization.policy_version, authorization.nonce,
            authorization.expires_at, json.dumps(list(authorization.scope)),
            authorization.signature,
        ),
    )
    conn.commit()


def consume_test_authorization(
    conn: sqlite3.Connection,
    issuer: TestAuthorizationIssuer,
    authorization: TestAuthorization,
    *,
    now: int,
    request_provenance: str,
    evolution_identity: str,
    parent_state_digest: str,
    policy_version: str,
) -> None:
    if not issuer.verify(authorization):
        raise PermissionError("invalid test authorization")
    if authorization.request_provenance != request_provenance or authorization.evolution_identity != evolution_identity:
        raise PermissionError("test authorization identity mismatch")
    if authorization.parent_state_digest != parent_state_digest or authorization.policy_version != policy_version:
        raise PermissionError("test authorization context mismatch")
    if now > authorization.expires_at:
        raise PermissionError("test authorization expired")
    row = conn.execute(
        "SELECT consumed, revoked FROM test_authorizations WHERE authorization_id = ?",
        (authorization.authorization_id,),
    ).fetchone()
    if row is None:
        raise PermissionError("test authorization is not persisted")
    if row[1]:
        raise PermissionError("test authorization revoked")
    if row[0]:
        raise PermissionError("test authorization already consumed")
    cur = conn.execute(
        "UPDATE test_authorizations SET consumed = 1 WHERE authorization_id = ? AND consumed = 0 AND revoked = 0",
        (authorization.authorization_id,),
    )
    if cur.rowcount != 1:
        raise PermissionError("test authorization consumption race")
    conn.commit()


def revoke_test_authorization(conn: sqlite3.Connection, authorization_id: str) -> None:
    cur = conn.execute(
        "UPDATE test_authorizations SET revoked = 1 WHERE authorization_id = ?",
        (authorization_id,),
    )
    if cur.rowcount != 1:
        raise KeyError("unknown test authorization")
    conn.commit()
