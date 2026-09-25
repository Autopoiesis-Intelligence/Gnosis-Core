from __future__ import annotations

import pytest

from gnosis.self_learning.collaboration_provider import normalize_provider_result


def test_provider_result_requires_observable_target_after():
    result = normalize_provider_result({"target_after": "revision-2", "id": "external-1"})
    assert result.target_after == "revision-2"
    assert result.result_metadata["id"] == "external-1"


@pytest.mark.parametrize("value", [None, {}, {"target_after": ""}, {"target_after": 7}])
def test_provider_result_rejects_missing_target_after(value):
    with pytest.raises((TypeError, ValueError)):
        normalize_provider_result(value)
