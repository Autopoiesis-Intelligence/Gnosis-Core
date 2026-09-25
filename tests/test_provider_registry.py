from __future__ import annotations

import pytest

from gnosis.self_learning.fake_external_provider import FakeExternalProvider
from gnosis.self_learning.provider_registry import TrustedProviderRegistry


def test_registry_returns_composition_owned_provider():
    provider = FakeExternalProvider()
    registry = TrustedProviderRegistry(_providers={"ci-fake": provider})
    assert registry.get("ci-fake") is provider


def test_registry_rejects_unknown_provider():
    registry = TrustedProviderRegistry(_providers={})
    with pytest.raises(LookupError):
        registry.get("attacker-provider")
