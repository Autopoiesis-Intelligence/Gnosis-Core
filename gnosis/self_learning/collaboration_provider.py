"""Capability contract for provider-specific external collaboration side effects.

The provider is intentionally a narrow capability: it accepts an already-authorized
action payload and returns observable post-action state. Application composition owns
the concrete provider. Requests cannot construct or replace it.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Protocol


class ExternalActionProvider(Protocol):
    def __call__(self, payload: Mapping[str, object]) -> Mapping[str, object]:
        """Perform exactly one external action and return observed result state."""


@dataclass(frozen=True)
class ProviderResult:
    target_after: str
    result_metadata: Mapping[str, object]


def normalize_provider_result(result: Mapping[str, object]) -> ProviderResult:
    if not isinstance(result, Mapping):
        raise TypeError("provider result must be a mapping")
    target_after = result.get("target_after")
    if not isinstance(target_after, str) or not target_after.strip():
        raise ValueError("provider result must contain target_after")
    return ProviderResult(target_after=target_after, result_metadata=dict(result))
