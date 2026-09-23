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


def _registry_digest(authorization: TestAuthorization, *, consumed: int = 0, revoked: int = 0, lifecycle_state: str = "active") -> str:
    return canonical_digest({**authorization.payload(), "consumed": consumed, "revoked": revoked, "lifecycle_state": lifecycle_state})


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
            integrity_digest TEXT NOT NULL,
            consumed INTEGER NOT NULL DEFAULT 0,
            revoked INTEGER NOT NULL DEFAULT 0,
            lifecycle_state TEXT NOT NULL DEFAULT "active",
            superseded_by TEXT
        )"""
    )
    for statement in (
        "ALTER TABLE test_authorizations ADD COLUMN integrity_digest TEXT",
        "ALTER TABLE test_authorizations ADD COLUMN lifecycle_state TEXT NOT NULL DEFAULT 'active'",
        "ALTER TABLE test_authorizations ADD COLUMN superseded_by TEXT",
    ):
        try:
            conn.execute(statement)
        except sqlite3.OperationalError:
            pass
    conn.commit()


def persist_test_authorization(conn: sqlite3.Connection, authorization: TestAuthorization) -> None:
    conn.execute(
        """INSERT INTO test_authorizations
        (authorization_id, issuer_id, issuer_version, request_provenance,
         evolution_identity, parent_state_digest, policy_version, nonce,
         expires_at, scope_json, signature, integrity_digest)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            authorization.authorization_id, authorization.issuer_id,
            authorization.issuer_version, authorization.request_provenance,
            authorization.evolution_identity, authorization.parent_state_digest,
            authorization.policy_version, authorization.nonce,
            authorization.expires_at, json.dumps(list(authorization.scope)),
            authorization.signature, _registry_digest(authorization),
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
        """SELECT issuer_id, issuer_version, request_provenance, evolution_identity,
                  parent_state_digest, policy_version, nonce, expires_at,
                  scope_json, signature, integrity_digest, consumed, revoked
           FROM test_authorizations WHERE authorization_id = ?""",
        (authorization.authorization_id,),
    ).fetchone()
    if row is None:
        raise PermissionError("test authorization is not persisted")
    if row[10] != _registry_digest(authorization, consumed=row[11], revoked=row[12], lifecycle_state=row[13]):
        raise PermissionError("test authorization registry integrity failure")
    stored = {
        "issuer_id": row[0], "issuer_version": row[1],
        "request_provenance": row[2], "evolution_identity": row[3],
        "parent_state_digest": row[4], "policy_version": row[5],
        "nonce": row[6], "expires_at": row[7],
        "scope": json.loads(row[8]), "signature": row[9],
    }
    expected = {
        "issuer_id": authorization.issuer_id,
        "issuer_version": authorization.issuer_version,
        "request_provenance": authorization.request_provenance,
        "evolution_identity": authorization.evolution_identity,
        "parent_state_digest": authorization.parent_state_digest,
        "policy_version": authorization.policy_version,
        "nonce": authorization.nonce,
        "expires_at": authorization.expires_at,
        "scope": list(authorization.scope),
        "signature": authorization.signature,
    }
    if stored != expected:
        raise PermissionError("test authorization registry payload mismatch")
    if row[12] or row[13] == "revoked":
        raise PermissionError("test authorization revoked")
    if row[11] or row[13] == "consumed":
        raise PermissionError("test authorization already consumed")
    new_digest = _registry_digest(authorization, consumed=1, revoked=0, lifecycle_state="consumed")
    cur = conn.execute(
        "UPDATE test_authorizations SET consumed = 1, lifecycle_state = "consumed", integrity_digest = ? WHERE authorization_id = ? AND consumed = 0 AND revoked = 0",
        (new_digest, authorization.authorization_id),
    )
    if cur.rowcount != 1:
        raise PermissionError("test authorization consumption race")
    conn.commit()


def revoke_test_authorization(conn: sqlite3.Connection, authorization_id: str) -> None:
    row = conn.execute("SELECT issuer_id, issuer_version, request_provenance, evolution_identity, parent_state_digest, policy_version, nonce, expires_at, scope_json, signature, consumed FROM test_authorizations WHERE authorization_id = ?", (authorization_id,)).fetchone()
    if row is None:
        raise KeyError("unknown test authorization")
    authorization = TestAuthorization(authorization_id=authorization_id, issuer_id=row[0], issuer_version=row[1], request_provenance=row[2], evolution_identity=row[3], parent_state_digest=row[4], policy_version=row[5], nonce=row[6], expires_at=row[7], scope=tuple(json.loads(row[8])), signature=row[9])
    new_digest = _registry_digest(authorization, consumed=row[10], revoked=1, lifecycle_state="revoked")
    cur = conn.execute(
        "UPDATE test_authorizations SET revoked = 1, lifecycle_state = "revoked", integrity_digest = ? WHERE authorization_id = ?",
        (new_digest, authorization_id),
    )
    if cur.rowcount != 1:
        raise KeyError("unknown test authorization")
    conn.commit()


def expire_test_authorization(
    conn: sqlite3.Connection,
    authorization: TestAuthorization,
    *,
    now: int,
) -> None:
    """Record expiry only as an observed lifecycle fact; never extend authority."""
    if now <= authorization.expires_at:
        raise ValueError("authorization is not expired")
    row = conn.execute(
        "SELECT consumed, revoked, integrity_digest FROM test_authorizations WHERE authorization_id = ?",
        (authorization.authorization_id,),
    ).fetchone()
    if row is None:
        raise KeyError("unknown test authorization")
    if row[2] != _registry_digest(authorization, consumed=row[0], revoked=row[1]):
        raise PermissionError("test authorization registry integrity failure")
    return None


def issue_for_provenance_for_test(
    issuer: TestAuthorizationIssuer,
    provenance: object,
    *,
    policy_version: str,
    expires_at: int,
    scope: tuple[str, ...] = ("test:execute",),
) -> TestAuthorization:
    """Issue only test authority from an exact provenance object."""
    return issuer.issue(
        request_provenance=str(provenance.provenance_id),
        evolution_identity=str(provenance.evolution_identity),
        parent_state_digest=str(provenance.parent_state_digest),
        policy_version=policy_version,
        scope=scope,
        expires_at=expires_at,
    )


def to_execution_authorization_for_test(
    issuer: TestAuthorizationIssuer,
    authorization: TestAuthorization,
):
    """Adapt verified test authority into the existing fail-closed boundary only."""
    if not issuer.verify(authorization):
        raise PermissionError("invalid test authorization")
    from .authority import ExecutionAuthorization
    return ExecutionAuthorization(
        request_provenance=authorization.request_provenance,
        owner_approved=True,
        evolution_identity=authorization.evolution_identity,
        approval_id=authorization.authorization_id,
    )
