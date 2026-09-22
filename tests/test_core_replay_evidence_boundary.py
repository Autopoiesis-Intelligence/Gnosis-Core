import ast
from pathlib import Path
ROOT=Path(__file__).parents[1]
def imports(p):
 t=ast.parse(p.read_text(encoding="utf-8")); o=set()
 for n in ast.walk(t):
  if isinstance(n,ast.Import): o.update(a.name for a in n.names)
  elif isinstance(n,ast.ImportFrom) and n.module:o.add(n.module)
 return o
def test_core_replay_uses_canonical_evidence():
 found=imports(ROOT/"gnosis/core/replay.py")
 assert "gnosis.evidence.provenance" in found
 assert "gnosis.evidence.audit" in found
 assert not any(x=="gnosis.core.provenance" or x.startswith("gnosis.core.provenance.") for x in found)
 assert not any(x=="gnosis.core.audit" or x.startswith("gnosis.core.audit.") for x in found)
