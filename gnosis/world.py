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



def _validate_representation_value(value: Any, path: str = "content") -> None:
    if value is None or isinstance(value, (str, bool, int, float)):
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise TypeError(f"{path} mapping keys must be strings")
            _validate_representation_value(item, f"{path}.{key}")
        return
    if isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            _validate_representation_value(item, f"{path}[{index}]")
        return
    raise TypeError(f"{path} contains unsupported value type: {type(value).__name__}")


@dataclass(frozen=True)
class Representation:
    """Immutable description of a content encoding/carrier."""

    encoding: str
    content: Any
    media_type: str | None = None

    def __post_init__(self) -> None:
        if not self.encoding.strip():
            raise ValueError("encoding must not be empty")
        _validate_representation_value(self.content)
        if self.media_type is not None and not self.media_type.strip():
            raise ValueError("media_type must not be empty when provided")
        object.__setattr__(self, "content", deep_freeze(self.content))

    @property
    def representation_id(self) -> str:
        return _stable_hash({
            "encoding": self.encoding,
            "content": self.content,
            "media_type": self.media_type,
        })

    @property
    def content_digest(self) -> str:
        return self.representation_id


@dataclass(frozen=True)
class Measurement:
    """Immutable quantitative interpretation; not an epistemic assertion."""

    quantity: str
    magnitude: int | float
    unit: str
    scale: str | None = None

    def __post_init__(self) -> None:
        if not self.quantity.strip():
            raise ValueError("quantity must not be empty")
        if not isinstance(self.magnitude, (int, float)) or isinstance(self.magnitude, bool):
            raise TypeError("magnitude must be a number")
        if not self.unit.strip():
            raise ValueError("unit must not be empty")
        if self.scale is not None and not self.scale.strip():
            raise ValueError("scale must not be empty when provided")

    @property
    def measurement_id(self) -> str:
        return _stable_hash({
            "quantity": self.quantity,
            "magnitude": self.magnitude,
            "unit": self.unit,
            "scale": self.scale,
        })


@dataclass(frozen=True)
class WorldRelation:
    """Immutable relation proposal between world-model objects.

    A relation records a typed connection; it does not assert that the
    connection is true or accepted.
    """

    subject_ref: str
    predicate: str
    object_ref: str
    context_ref: str | None = None

    def __post_init__(self) -> None:
        if not self.subject_ref.strip():
            raise ValueError("subject_ref must not be empty")
        if not self.predicate.strip():
            raise ValueError("predicate must not be empty")
        if not self.object_ref.strip():
            raise ValueError("object_ref must not be empty")
        if self.context_ref is not None and not self.context_ref.strip():
            raise ValueError("context_ref must be empty or omitted")

    @property
    def relation_id(self) -> str:
        return _stable_hash({
            "subject_ref": self.subject_ref,
            "predicate": self.predicate,
            "object_ref": self.object_ref,
            "context_ref": self.context_ref,
        })


@dataclass(frozen=True)
class EpistemicTransition:
    """Immutable record of an epistemic state transition.

    The transition records a claim about state change; it does not mutate the
    referenced world object and does not itself make the target state true.
    """

    subject_ref: str
    from_state: str
    to_state: str
    basis_refs: Sequence[str] = field(default_factory=tuple)
    reason_ref: str | None = None

    def __post_init__(self) -> None:
        if not self.subject_ref.strip():
            raise ValueError("subject_ref must not be empty")
        if not self.from_state.strip():
            raise ValueError("from_state must not be empty")
        if not self.to_state.strip():
            raise ValueError("to_state must not be empty")
        if not all(isinstance(ref, str) and ref.strip() for ref in self.basis_refs):
            raise TypeError("basis_refs must contain non-empty string references")
        if self.reason_ref is not None and not self.reason_ref.strip():
            raise ValueError("reason_ref must be empty or omitted")
        object.__setattr__(self, "basis_refs", tuple(self.basis_refs))

    @property
    def transition_id(self) -> str:
        return _stable_hash({
            "subject_ref": self.subject_ref,
            "from_state": self.from_state,
            "to_state": self.to_state,
            "basis_refs": self.basis_refs,
            "reason_ref": self.reason_ref,
        })
