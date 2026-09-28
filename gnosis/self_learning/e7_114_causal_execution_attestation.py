"""E7 causal execution attestation for locked implementation paths."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import json
import os
import tempfile

@dataclass(frozen=True)
class CausalExecutionAttestation:
    executed_paths: tuple[str, ...]
    required_paths: tuple[str, ...]
    evidence_digest: str
    status: str

def _normal(path: str) -> str:
    return str(Path(path).resolve())

def run_with_causal_trace(argv, *, repository_root: str | Path, cwd: str | Path, env: dict[str, str]):
    root = Path(repository_root).resolve()
    with tempfile.TemporaryDirectory(prefix="e7-causal-") as td:
        trace_file = Path(td) / "trace.json"
        site = Path(td) / "sitecustomize.py"
        site.write_text(
            "import atexit, json, os, sys\n"
            f"_root={root.as_posix()!r}\n"
            f"_out={trace_file.as_posix()!r}\n"
            "_seen=set()\n"
            "def _trace(frame,event,arg):\n"
            "    if event=='line':\n"
            "        p=os.path.abspath(frame.f_code.co_filename)\n"
            "        if p.startswith(_root + os.sep): _seen.add(os.path.relpath(p,_root))\n"
            "    return _trace\n"
            "sys.settrace(_trace)\n"
            "atexit.register(lambda: open(_out,'w',encoding='utf-8').write(json.dumps(sorted(_seen))))\n",
            encoding="utf-8",
        )
        child_env = dict(env)
        child_env["PYTHONPATH"] = td + os.pathsep + child_env.get("PYTHONPATH", "")
        import subprocess
        completed = subprocess.run(argv, cwd=cwd, capture_output=True, text=True, check=False, env=child_env)
        executed = tuple(json.loads(trace_file.read_text(encoding="utf-8"))) if trace_file.exists() else ()
        return completed, executed

def attest_causal_execution(*, executed_paths: tuple[str, ...], required_paths: tuple[str, ...]) -> CausalExecutionAttestation:
    executed = tuple(sorted(set(executed_paths)))
    required = tuple(required_paths)
    missing = [p for p in required if p not in executed]
    payload = json.dumps({"executed_paths": executed, "required_paths": required, "missing": missing}, sort_keys=True, separators=(",", ":"))
    from hashlib import sha256
    return CausalExecutionAttestation(executed, required, sha256(payload.encode()).hexdigest(), "PASS" if not missing else "FAIL")
