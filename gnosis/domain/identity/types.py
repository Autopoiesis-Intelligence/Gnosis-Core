from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class Identity:
    actor_id: str
    tenant_id: str
    issuer: str
    roles: tuple[str, ...]
    issued_at_ms: int
    expires_at_ms: int
