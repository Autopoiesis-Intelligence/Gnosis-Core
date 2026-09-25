"""Deterministic provider for CI-only governed execution tests."""
from __future__ import annotations

from typing import Mapping


class FakeExternalProvider:
    def __init__(self, *, target_after: str = "target-r2", fail: bool = False) -> None:
        self.calls: list[Mapping[str, object]] = []
        self.target_after = target_after
        self.fail = fail

    def __call__(self, payload: Mapping[str, object]) -> Mapping[str, object]:
        self.calls.append(dict(payload))
        if self.fail:
            raise RuntimeError("fake provider failure")
        return {"target_after": self.target_after, "provider": "fake-ci"}
