from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "gnosis" / "self_learning"
ALLOWED_PROVIDER_FILES = {
    "provider_registry.py",
    "fake_external_provider.py",
    "governed_external_adapter.py",
    "collaboration_provider.py",
}


def _tree(path: Path) -> ast.AST:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def test_provider_symbols_are_imported_only_by_governed_boundary():
    violations: list[str] = []
    for path in PACKAGE.rglob("*.py"):
        if path.name in ALLOWED_PROVIDER_FILES:
            continue
        tree = _tree(path)
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                if "collaboration_provider" in node.module or "provider_registry" in node.module:
                    violations.append(f"{path}:{node.lineno}:{node.module}")
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if "collaboration_provider" in alias.name or "provider_registry" in alias.name:
                        violations.append(f"{path}:{node.lineno}:{alias.name}")
    assert violations == []


def test_only_governed_adapter_contains_provider_call_syntax():
    violations: list[str] = []
    for path in PACKAGE.rglob("*.py"):
        if path.name == "governed_external_adapter.py":
            continue
        tree = _tree(path)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "provider":
                violations.append(f"{path}:{node.lineno}")
    assert violations == []
