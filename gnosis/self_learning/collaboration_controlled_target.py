"""Controlled local target for the E7.77 causal execution gate.

This target is deliberately local and deterministic. It is an effect boundary,
not an authorization or evidence authority.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Mapping, Protocol


class ExternalActionPort(Protocol):
    """Narrow effect-only port owned by the collaboration runtime."""

    def execute(self, request: object) -> "ControlledExecutionObservation": ...


def _digest(value: Mapping[str, object]) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class ControlledTargetSnapshot:
    resource_id: str
    revision: str
    content_digest: str


@dataclass(frozen=True)
class ControlledExecutionObservation:
    target_before: ControlledTargetSnapshot
    target_after: ControlledTargetSnapshot
    effect_applied: bool


class ControlledTarget:
    """Small mutable local target used only behind an explicit effect port."""

    def __init__(self, resource_id: str, initial_state: Mapping[str, object]) -> None:
        if not resource_id.strip():
            raise ValueError("resource_id is required")
        self._resource_id = resource_id
        self._state = dict(initial_state)
        self._revision = 0

    def snapshot(self) -> ControlledTargetSnapshot:
        return ControlledTargetSnapshot(
            resource_id=self._resource_id,
            revision=f"r{self._revision}",
            content_digest=_digest(self._state),
        )

    def apply(self, parameters: Mapping[str, object]) -> ControlledExecutionObservation:
        before = self.snapshot()
        updated = dict(self._state)
        updated.update(parameters)
        if updated == self._state:
            return ControlledExecutionObservation(before, before, False)
        self._state = updated
        self._revision += 1
        after = self.snapshot()
        return ControlledExecutionObservation(before, after, True)


class ControlledTargetAdapter:
    """Adapter implementing the effect-only port for a controlled target."""

    def __init__(self, target: ControlledTarget) -> None:
        self._target = target

    def execute(self, request: object) -> ControlledExecutionObservation:
        parameters = getattr(request, "parameters", None)
        if not isinstance(parameters, Mapping):
            raise TypeError("request parameters must be a mapping")
        return self._target.apply(parameters)
