"""Adversarial tests for the self-optimization resource boundary."""
from __future__ import annotations

from gnosis.evolution.sandbox import SandboxBudget


def test_resource_budget_rejects_invalid_memory_limit() -> None:
    try:
        SandboxBudget(max_memory_bytes=0)
    except ValueError as exc:
        assert "max_memory_bytes" in str(exc)
    else:
        raise AssertionError("invalid memory budget was accepted")


def test_resource_budget_allows_explicit_memory_limit() -> None:
    budget = SandboxBudget(max_operations=2, timeout_seconds=0.5, max_memory_bytes=1024)
    assert budget.max_operations == 2
    assert budget.max_memory_bytes == 1024
