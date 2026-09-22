from pathlib import Path


def test_research_reference_is_data_not_importable_runtime_authority():
    root = Path(__file__).resolve().parents[1]
    forbidden = ("from Gnozis import", "import Gnozis", "from research", "import research")
    for path in (root / "gnosis").rglob("*.py"):
        source = path.read_text(encoding="utf-8")
        assert not any(token in source for token in forbidden), path


def test_canonical_tree_contains_no_research_repository_checkout():
    root = Path(__file__).resolve().parents[1]
    forbidden_names = {"Gnozis", "research", "development"}
    for path in root.iterdir():
        assert path.name not in forbidden_names, path


def test_research_reference_documents_are_non_authoritative_contracts():
    root = Path(__file__).resolve().parents[1]
    docs = list((root / "docs").glob("*RESEARCH*"))
    assert docs
    for doc in docs:
        text = doc.read_text(encoding="utf-8").lower()
        assert "without importing the record's authority" in text or "non-authoritative" in text or "must not" in text

import ast

def test_research_references_are_opaque_and_cannot_be_used_as_imports():
    root = Path(__file__).resolve().parents[1] / "gnosis"
    for path in root.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                names = [a.name for a in node.names]
                module = node.module if isinstance(node, ast.ImportFrom) else ""
                assert not any(
                    n == "Gnozis" or n.startswith("Gnozis.") or
                    n == "research" or n.startswith("research.")
                    for n in names + ([module] if module else [])
                ), path

def test_runtime_configuration_does_not_reference_external_research_paths():
    root = Path(__file__).resolve().parents[1]
    forbidden_fragments = ("GNOZIS_RESEARCH", "RESEARCH_REPO", "RESEARCH_PATH", "DEVELOPMENT_REPO")
    for path in root.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        assert not any(fragment in text for fragment in forbidden_fragments), path
