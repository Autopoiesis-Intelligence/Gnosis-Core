from __future__ import annotations

from dataclasses import dataclass
from typing import Final

CapabilityToken = str

ALLOWED_CAPABILITIES: Final[frozenset[str]] = frozenset({
    "control:policy:read",
    "control:policy:evaluate",
    "evidence:event:append",
    "state:candidate:propose",
    "state:test:execute",
    "state:verify:evaluate",
    "state:commit:apply",
})

@dataclass(frozen=True)
class Capabilities:
    granted_capabilities: tuple[CapabilityToken, ...]
    constraints: tuple[tuple[str, str | int | bool], ...] = ()
