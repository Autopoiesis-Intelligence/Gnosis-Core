from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "gnosis" / "self_learning"
BOUNDARY = "governed_external_adapter.py"
PUBLIC_ENTRYPOINT = "collaboration_entrypoint.py"


def _parse(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def test_public_entrypoint_does_not_accept_provider_as_request_input():
    tree = _parse(PACKAGE / PUBLIC_ENTRYPOINT)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            args = [a.arg for a in node.args.args]
            assert "provider" not in args
            assert "external_provider" not in args


def test_non_boundary_modules_do_not_expose_provider_parameters():
    violations: list[str] = []
    for path in PACKAGE.rglob("*.py"):
        if path.name in {
            BOUNDARY,
            "provider_registry.py",
            "fake_external_provider.py",
            "collaboration_provider.py",
        }:
            continue
        tree = _parse(path)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                args = [a.arg for a in node.args.args]
                for name in ("provider", "external_provider", "provider_registry"):
                    if name in args:
                        violations.append(f"{path}:{node.lineno}:{name}")
    assert violations == []


def test_public_entrypoint_delegates_to_owned_runtime_only():
    source = (PACKAGE / PUBLIC_ENTRYPOINT).read_text(encoding="utf-8")
    assert "self.runtime.execute" in source
    assert "provider(" not in source
