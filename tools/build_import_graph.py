from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "gnosis"


def local_module_names() -> set[str]:
    names = set()
    for p in ROOT.rglob("*.py"):
        rel = p.relative_to(ROOT).with_suffix("")
        if rel.name == "__init__":
            rel = rel.parent
        names.add("gnosis." + ".".join(rel.parts))
    return names


def imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    result = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            result.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                base = path.relative_to(ROOT).with_suffix("")
                parts = list(base.parts[:-1])
                if node.level > len(parts):
                    continue
                parts = parts[: len(parts) - node.level + 1]
                if node.module:
                    parts.extend(node.module.split("."))
                result.add("gnosis." + ".".join(parts))
            elif node.module:
                result.add(node.module)
    return result


if __name__ == "__main__":
    local = local_module_names()
    for path in sorted(ROOT.rglob("*.py")):
        for target in sorted(imports(path)):
            if target in local or target.startswith("gnosis."):
                print(f"{path.relative_to(ROOT)} -> {target}")
