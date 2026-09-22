import ast
from pathlib import Path
ROOT=Path(__file__).parents[1]
def imports(p):
 t=ast.parse(p.read_text(encoding="utf-8")); o=set()
 for n in ast.walk(t):
  if isinstance(n,ast.Import): o.update(a.name for a in n.names)
  elif isinstance(n,ast.ImportFrom) and n.module:o.add(n.module)
 return o
def test_core_evidence_compatibility_paths_have_single_canonical_source():
 for name in ("provenance.py","audit.py"):
  found=imports(ROOT/"gnosis/core"/name)
  assert any(x.startswith("gnosis.evidence.") for x in found)

def test_canonical_evidence_has_no_core_dependency():
 for p in (ROOT/"gnosis/evidence").glob("*.py"):
  found=imports(p)
  assert not any(x=="gnosis.core" or x.startswith("gnosis.core.") for x in found)
