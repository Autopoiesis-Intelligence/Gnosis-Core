import ast
from pathlib import Path
ROOT=Path(__file__).parents[1]
def imports(p):
 t=ast.parse(p.read_text(encoding="utf-8")); o=set()
 for n in ast.walk(t):
  if isinstance(n,ast.Import): o.update(a.name for a in n.names)
  elif isinstance(n,ast.ImportFrom) and n.module:o.add(n.module)
 return o
def test_storage_recovery_does_not_depend_on_reflection_persistence():
 found=imports(ROOT/"gnosis/storage/recovery_adapter.py")
 assert "gnosis.reflection.persistence" not in found
 assert "gnosis.evidence.recovery" in found
