import os
import subprocess
import sys
from pathlib import Path


def test_core_package_imports_without_research_environment():
    root = Path(__file__).resolve().parents[1]
    env = dict(os.environ)
    for key in tuple(env):
        if "RESEARCH" in key.upper() or "DEVELOPMENT" in key.upper():
            env.pop(key)
    env["PYTHONPATH"] = str(root)
    code = (
        "from gnosis.core import State, ExecutionInput, ExecutionIdentity; "
        "print(State.__name__, ExecutionInput.__name__, ExecutionIdentity.__name__)"
    )
    result = subprocess.run(
        [sys.executable, "-I", "-c", code],
        cwd=root,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def test_project_core_has_no_runtime_dependencies():
    pyproject = (Path(__file__).resolve().parents[1] / "pyproject.toml").read_text(
        encoding="utf-8"
    )
    assert "dependencies = []" in pyproject
