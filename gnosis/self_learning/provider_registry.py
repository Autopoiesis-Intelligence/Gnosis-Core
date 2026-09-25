"""Composition-owned registry for governed external providers."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from .collaboration_provider import ExternalActionProvider


@dataclass(frozen=True)
class TrustedProviderRegistry:
    _providers: Mapping[str, ExternalActionProvider]

    def get(self, provider_id: str) -> ExternalActionProvider:
        provider = self._providers.get(provider_id)
        if provider is None:
            raise LookupError(f"unknown external provider: {provider_id}")
        return provider
