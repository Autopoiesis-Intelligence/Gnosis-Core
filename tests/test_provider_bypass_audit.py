from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "gnosis" / "self_learning"


def _python_sources() -> list[str]:
    return [
        path.read_text(encoding="utf-8")
        for path in PACKAGE.rglob("*.py")
        if path.name not in {"provider_registry.py", "fake_external_provider.py", "governed_external_adapter.py"}
    ]


def test_production_sources_do_not_construct_or_invoke_provider_directly():
    forbidden = (
        "ExternalActionProvider(",
        "FakeExternalProvider(",
        "provider(payload)",
        "provider(",
    )
    violations = []
    for source in _python_sources():
        for token in forbidden:
            if token in source:
                violations.append(token)
    assert violations == []
