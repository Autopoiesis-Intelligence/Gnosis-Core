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

def test_end_to_end_persistence_recovery_and_diagnostic_path_is_canonical():
    from diagnostic_corpus.generate import generate
    generate()
    root = Path(__file__).resolve().parents[1] / "diagnostic_corpus" / "SELF-DIAGNOSTIC-0001"
    assert (root / "diagnostic.json").exists()
    assert (root / "transitions.json").exists()
    assert (root / "metadata.json").exists()


def test_release_workflow_has_unique_required_test_modules():
    workflow = (Path(__file__).resolve().parents[1] / ".github" / "workflows" / "self-diagnostic.yml").read_text(encoding="utf-8")
    run_line = next(line for line in workflow.splitlines() if line.strip().startswith("run: pytest"))
    modules = run_line.split("pytest -q", 1)[1].split()
    assert len(modules) == len(set(modules))
    required = {
        "tests/test_execution_input.py",
        "tests/test_execution_identity.py",
        "tests/test_research_authority_boundary.py",
        "tests/test_recovery_clean_room.py",
        "tests/test_clean_room_release.py",
        "tests/test_diagnostic_execution.py",
        "tests/test_persistence_crash_reopen.py",
        "tests/test_transition_replay_idempotency.py",
    }
    assert required.issubset(modules)
