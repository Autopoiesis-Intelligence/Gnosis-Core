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


def build_graph() -> dict[str, set[str]]:
    local = local_module_names()
    graph = {}
    for path in sorted(ROOT.rglob("*.py")):
        source = "gnosis." + ".".join(path.relative_to(ROOT).with_suffix("").parts)
        graph[source] = {target for target in imports(path) if target in local}
    return graph


def find_cycles(graph: dict[str, set[str]]) -> list[list[str]]:
    cycles = []
    stack = []
    active = set()

    def visit(node: str):
        if node in active:
            if node in stack:
                cycles.append(stack[stack.index(node):] + [node])
            return
        active.add(node)
        stack.append(node)
        for child in graph.get(node, set()):
            visit(child)
        stack.pop()
        active.remove(node)

    for node in graph:
        visit(node)
    return cycles


if __name__ == "__main__":
    graph = build_graph()
    for source, targets in sorted(graph.items()):
        for target in sorted(targets):
            print(f"{source} -> {target}")
    cycles = find_cycles(graph)
    print("CYCLES:", len(cycles))
    for cycle in cycles:
        print(" -> ".join(cycle))
