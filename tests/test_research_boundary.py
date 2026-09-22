import ast
from pathlib import Path

ROOT=Path(__file__).parents[1]

def imports(path):
    tree=ast.parse(path.read_text(encoding="utf-8")); out=set()
    for n in ast.walk(tree):
        if isinstance(n,ast.Import): out.update(a.name for a in n.names)
        elif isinstance(n,ast.ImportFrom) and n.module: out.add(n.module)
    return out

def test_evolution_recovery_does_not_depend_on_reflection_persistence():
    imports_found=imports(ROOT/"gnosis/evolution/recovery.py")
    assert "gnosis.reflection.persistence" not in imports_found
    assert "gnosis.evidence.recovery" in imports_found

def test_evidence_recovery_does_not_depend_on_research_machine():
    for path in (ROOT/"gnosis/evidence").glob("*.py"):
        found=imports(path)
        assert not any(x=="gnosis.reflection" or x.startswith("gnosis.reflection.") for x in found)
        assert not any(x=="gnosis.evolution" or x.startswith("gnosis.evolution.") for x in found)
