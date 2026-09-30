"""Minimal immutable World Model primitives.

R1 contract: WorldObservation records an observation without asserting
epistemic truth. Epistemic status is represented separately by future
EpistemicTransition records.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from gnosis.core.types import _stable_hash, deep_freeze


@dataclass(frozen=True)
class WorldObservation:
    """Immutable registration of an observation about a bounded context.

    Identity is content-derived and deliberately excludes epistemic status.
    Acceptance, rejection, supersession and other epistemic changes belong
    to separate immutable transition records.
    """

    context_ref: str
    distinction: str
    carrier_ref: str | None = None
    properties: Mapping[str, Any] = field(default_factory=dict)
    relations: Sequence[str] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.context_ref.strip():
            raise ValueError("context_ref must not be empty")
        if not self.distinction.strip():
            raise ValueError("distinction must not be empty")
        object.__setattr__(self, "properties", deep_freeze(dict(self.properties)))
        object.__setattr__(self, "relations", tuple(self.relations))

    @property
    def observation_id(self) -> str:
        return _stable_hash({
            "context_ref": self.context_ref,
            "distinction": self.distinction,
            "carrier_ref": self.carrier_ref,
            "properties": self.properties,
            "relations": self.relations,
        })

    @property
    def content_digest(self) -> str:
        return self.observation_id
