"""Canonical persistence boundary for externally issued owner authorization.

Persistence records authority evidence and enforces one-time consumption.
It does not issue authority and does not execute work.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3

from .owner_authorization import OwnerAuthorizationV1


def _record_digest(authorization: OwnerAuthorizationV1, *, consumed: int, revoked: int) -> str:
    payload = {
        "authorization_id": authorization.authorization_id,
        "nonce": authorization.nonce,
        "issuer_id": authorization.issuer_id,
        "key_version": authorization.key_version,
        "authority_root": authorization.authority_root,
        "scope": authorization.scope,
        "policy_version": authorization.policy_version,
        "request_provenance": authorization.request_provenance,
        "evolution_identity": authorization.evolution_identity,
        "parent_state_digest": authorization.parent_state_digest,
        "evidence_digest": authorization.evidence_digest,
        "valid_from": authorization.valid_from,
        "valid_until": authorization.valid_until,
        "signature": authorization.signature.hex(),
        "consumed": consumed,
        "revoked": revoked,
    }
    return "sha256:" + hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def persist_owner_authorization(conn: sqlite3.Connection, authorization: OwnerAuthorizationV1) -> None:
    digest = _record_digest(authorization, consumed=0, revoked=0)
    conn.execute(
        """INSERT INTO owner_authorizations
        (authorization_id,nonce,issuer_id,key_version,authority_root,scope,policy_version,
         request_provenance,evolution_identity,parent_state_digest,evidence_digest,
         valid_from,valid_until,signature,consumed,revoked,integrity_digest)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,0,0,?)""",
        (
            authorization.authorization_id, authorization.nonce, authorization.issuer_id,
            authorization.key_version, authorization.authority_root, authorization.scope,
            authorization.policy_version, authorization.request_provenance,
            authorization.evolution_identity, authorization.parent_state_digest,
            authorization.evidence_digest, authorization.valid_from, authorization.valid_until,
            authorization.signature, digest,
        ),
    )


def consume_owner_authorization(
    conn: sqlite3.Connection,
    authorization: OwnerAuthorizationV1,
) -> None:
    row = conn.execute(
        """SELECT authorization_id,nonce,issuer_id,key_version,authority_root,scope,
                  policy_version,request_provenance,evolution_identity,parent_state_digest,
                  evidence_digest,valid_from,valid_until,signature,consumed,revoked,
                  integrity_digest
           FROM owner_authorizations WHERE authorization_id=?""",
        (authorization.authorization_id,),
    ).fetchone()
    if row is None:
        raise PermissionError("owner authorization is not persisted")

    stored = OwnerAuthorizationV1(
        issuer_id=row[2], key_version=row[3], authority_root=row[4], scope=row[5],
        policy_version=row[6], request_provenance=row[7], evolution_identity=row[8],
        parent_state_digest=row[9], evidence_digest=row[10], authorization_id=row[0],
        nonce=row[1], valid_from=row[11], valid_until=row[12], signature=bytes(row[13]),
    )
    if row[16] != _record_digest(stored, consumed=row[14], revoked=row[15]):
        raise PermissionError("owner authorization persistence integrity failure")
    if stored.canonical_payload != authorization.canonical_payload or stored.signature != authorization.signature:
        raise PermissionError("owner authorization persistence payload mismatch")
    if row[15]:
        raise PermissionError("owner authorization revoked")
    if row[14]:
        raise PermissionError("owner authorization already consumed")

    digest = _record_digest(authorization, consumed=1, revoked=0)
    cur = conn.execute(
        """UPDATE owner_authorizations
           SET consumed=1, integrity_digest=?
           WHERE authorization_id=? AND nonce=? AND consumed=0 AND revoked=0""",
        (digest, authorization.authorization_id, authorization.nonce),
    )
    if cur.rowcount != 1:
        raise PermissionError("owner authorization consumption race")


def load_owner_authorization(
    conn: sqlite3.Connection,
    authorization_id: str,
) -> OwnerAuthorizationV1:
    row = conn.execute(
        """SELECT authorization_id,nonce,issuer_id,key_version,authority_root,scope,
                  policy_version,request_provenance,evolution_identity,parent_state_digest,
                  evidence_digest,valid_from,valid_until,signature,consumed,revoked,
                  integrity_digest
           FROM owner_authorizations WHERE authorization_id=?""",
        (authorization_id,),
    ).fetchone()
    if row is None:
        raise KeyError(authorization_id)
    authorization = OwnerAuthorizationV1(
        issuer_id=row[2], key_version=row[3], authority_root=row[4], scope=row[5],
        policy_version=row[6], request_provenance=row[7], evolution_identity=row[8],
        parent_state_digest=row[9], evidence_digest=row[10], authorization_id=row[0],
        nonce=row[1], valid_from=row[11], valid_until=row[12], signature=bytes(row[13]),
    )
    if row[16] != _record_digest(authorization, consumed=row[14], revoked=row[15]):
        raise RuntimeError("owner authorization persistence integrity failure")
    return authorization
