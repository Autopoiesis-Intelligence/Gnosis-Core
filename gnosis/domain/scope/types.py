from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class Scope:
    scope_id: str
    tenant_id: str
    allowed_resources: tuple[str, ...]
    restricted_paths: tuple[str, ...] = ()
    valid_until_ms: int = 0
    rate_limit_key: str | None = None
