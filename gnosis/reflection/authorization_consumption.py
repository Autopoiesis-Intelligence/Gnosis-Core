"""Fail-closed durable consumption boundary for execution authorizations."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class AuthorizationConsumption:
    authorization_id: str
    request_provenance: str
    evolution_identity: str
    policy_version: str
    consumed: bool

def consume_authorization_in_transaction(conn, authorization_id: str, *, request_provenance: str, evolution_identity: str, policy_version: str, actor: str) -> AuthorizationConsumption:
    """Consume inside the caller's transaction; never opens a nested transaction."""
    if not all(isinstance(x, str) and x.strip() for x in (authorization_id, request_provenance, evolution_identity, policy_version, actor)):
        raise PermissionError("authorization consumption input is incomplete")
    from gnosis.storage.repositories import append_audit, verify_audit_chain
    event_key = f"execution-authorization:{authorization_id}"
    existing = conn.execute("SELECT event_hash FROM audit_events WHERE event_id=?", (event_key,)).fetchone()
    if existing is not None:
        raise PermissionError("execution authorization already consumed")
    append_audit(conn, actor=actor, action="execution.authorization.consume", resource=authorization_id, result="accepted", event_key=event_key)
    verify_audit_chain(conn)
    return AuthorizationConsumption(authorization_id, request_provenance, evolution_identity, policy_version, True)

def consume_authorization(conn, authorization_id: str, *, request_provenance: str, evolution_identity: str, policy_version: str, actor: str) -> AuthorizationConsumption:
    """Convenience wrapper retaining the standalone atomic transaction API."""
    from gnosis.storage.database import transaction
    with transaction(conn):
        return consume_authorization_in_transaction(conn, authorization_id, request_provenance=request_provenance, evolution_identity=evolution_identity, policy_version=policy_version, actor=actor)
