import ast
from pathlib import Path


def test_recovery_module_has_no_research_or_development_imports():
    root = Path(__file__).resolve().parents[1] / "gnosis"
    for path in root.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                names = [a.name for a in node.names]
                module = node.module if isinstance(node, ast.ImportFrom) else ""
                assert not any(
                    n == "research" or n.startswith("research.") or
                    n == "development" or n.startswith("development.") or
                    n == "Gnozis" or n.startswith("Gnozis.")
                    for n in names + ([module] if module else [])
                ), path


def test_recovery_source_files_are_inside_canonical_tree():
    root = Path(__file__).resolve().parents[1]
    recovery_files = list((root / "gnosis").rglob("*recover*.py"))
    assert recovery_files
    for path in recovery_files:
        assert root in path.parents


def test_recovery_contract_has_no_external_repository_parameter():
    root = Path(__file__).resolve().parents[1] / "gnosis"
    forbidden = ("research_repo", "research_path", "development_repo", "development_path")
    for path in root.rglob("*.py"):
        source = path.read_text(encoding="utf-8")
        assert not any(token in source for token in forbidden), path
