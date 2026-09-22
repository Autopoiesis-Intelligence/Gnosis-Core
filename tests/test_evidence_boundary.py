from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).parents[1]


def _imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            found.add(node.module)
    return found


def test_canonical_evidence_does_not_depend_on_experimental_evolution() -> None:
    for path in (ROOT / "gnosis" / "evidence").glob("*.py"):
        imports = _imports(path)
        assert not any(name == "gnosis.evolution" or name.startswith("gnosis.evolution.") for name in imports)


def test_reflection_persistence_uses_canonical_evidence_boundary() -> None:
    imports = _imports(ROOT / "gnosis" / "reflection" / "persistence.py")
    assert "gnosis.evidence.provenance" in imports
    assert "gnosis.evidence.audit" in imports
    assert "gnosis.evolution.provenance" not in imports
    assert "gnosis.evolution.audit" not in imports


def test_legacy_evolution_paths_are_compatibility_only() -> None:
    for name in ("provenance.py", "audit.py"):
        imports = _imports(ROOT / "gnosis" / "evolution" / name)
        assert any(item.startswith("gnosis.evidence.") for item in imports)
