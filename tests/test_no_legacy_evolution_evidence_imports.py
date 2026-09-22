import ast
from pathlib import Path
ROOT=Path(__file__).parents[1]
def imports(p):
 t=ast.parse(p.read_text(encoding="utf-8")); o=set()
 for n in ast.walk(t):
  if isinstance(n,ast.Import): o.update(a.name for a in n.names)
  elif isinstance(n,ast.ImportFrom) and n.module:o.add(n.module)
 return o
def test_evolution_has_no_legacy_canonical_evidence_imports():
 for p in (ROOT/"gnosis/evolution").glob("*.py"):
  found=imports(p)
  assert not any(x.startswith("gnosis.evolution.provenance") or x.startswith("gnosis.evolution.audit") for x in found)
