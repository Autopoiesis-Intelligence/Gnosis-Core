"""Core-boundary one-time consumption guard for Federation handoffs."""
from dataclasses import dataclass, field
from threading import Lock

@dataclass
class HandoffReplayGuard:
    _consumed: set[str] = field(default_factory=set)
    _lock: Lock = field(default_factory=Lock, repr=False)

    def consume(self, handoff_sha256: str) -> dict:
        if not handoff_sha256:
            return {"result":"REJECT","errors":["missing_handoff_digest"]}
        with self._lock:
            if handoff_sha256 in self._consumed:
                return {"result":"REJECT","errors":["handoff_replay"]}
            self._consumed.add(handoff_sha256)
            return {"result":"ACCEPT","handoff_sha256":handoff_sha256}

    def consume_durable(self, conn, *, handoff_sha256: str, actor: str) -> dict:
        """Consume exactly once through the canonical Core audit transaction.

        The audit ledger is the durable authority; this guard does not create a
        second persistence store. Duplicate handoff IDs fail closed.
        """
        if not handoff_sha256:
            return {"result":"REJECT","errors":["missing_handoff_digest"]}
        if not isinstance(actor, str) or not actor.strip():
            return {"result":"REJECT","errors":["missing_actor"]}
        from gnosis.storage.database import transaction
        from gnosis.storage.repositories import append_audit, verify_audit_chain
        event_key = f"federation-handoff:{handoff_sha256}"
        with transaction(conn):
            existing = conn.execute("SELECT event_hash FROM audit_events WHERE event_id=?", (event_key,)).fetchone()
            if existing is not None:
                return {"result":"REJECT","errors":["handoff_replay"],"audit_event_hash":existing[0]}
            audit_hash = append_audit(conn, actor=actor, action="federation.handoff.consume", resource=handoff_sha256, result="accepted", event_key=event_key)
            verify_audit_chain(conn)
            return {"result":"ACCEPT","handoff_sha256":handoff_sha256,"audit_event_hash":audit_hash}

    def contains(self, handoff_sha256: str) -> bool:
        with self._lock:
            return handoff_sha256 in self._consumed
