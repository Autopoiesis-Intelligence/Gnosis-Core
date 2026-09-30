"""Minimal immutable World Model primitives."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from gnosis.core.types import _stable_hash, deep_freeze


def _validate_world_value(value: Any, path: str = "value") -> None:
    if value is None or isinstance(value, (str, bool, int, float)):
        return
    if isinstance(value, Mapping):
        for key, item in value.items():
            if not isinstance(key, str):
                raise TypeError(f"{path} mapping keys must be strings")
            _validate_world_value(item, f"{path}.{key}")
        return
    if isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            _validate_world_value(item, f"{path}[{index}]")
        return
    raise TypeError(f"{path} contains unsupported value type: {type(value).__name__}")


@dataclass(frozen=True)
class WorldObservation:
    """Immutable registration of an observation without epistemic truth."""

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
        _validate_world_value(self.properties, "properties")
        if not all(isinstance(ref, str) for ref in self.relations):
            raise TypeError("relations must contain only string references")
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
