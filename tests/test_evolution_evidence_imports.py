import ast
from pathlib import Path
ROOT=Path(__file__).parents[1]
def imports(path):
 t=ast.parse(path.read_text(encoding="utf-8")); out=set()
 for n in ast.walk(t):
  if isinstance(n,ast.Import): out.update(a.name for a in n.names)
  elif isinstance(n,ast.ImportFrom) and n.module: out.add(n.module)
 return out
def test_evolution_public_and_diagnostic_paths_use_canonical_evidence():
 for name in ("__init__.py","diagnostic_adapter.py","diagnostic_admission.py"):
  found=imports(ROOT/"gnosis/evolution"/name)
  assert not any(x=="gnosis.evolution.provenance" or x.startswith("gnosis.evolution.provenance.") for x in found)
  if name!="__init__.py": assert "gnosis.evidence.provenance" in found
