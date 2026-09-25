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

    def contains(self, handoff_sha256: str) -> bool:
        with self._lock:
            return handoff_sha256 in self._consumed
