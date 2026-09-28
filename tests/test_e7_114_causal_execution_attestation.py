import json
from pathlib import Path

from gnosis.self_learning.e7_114_causal_execution_attestation import attest_causal_execution, run_with_causal_trace


def test_causal_attestation_requires_every_implementation_path():
    passed = attest_causal_execution(executed_paths=("gnosis/a.py", "tests/t.py"), required_paths=("gnosis/a.py",))
    assert passed.status == "PASS"
    failed = attest_causal_execution(executed_paths=("tests/t.py",), required_paths=("gnosis/a.py",))
    assert failed.status == "FAIL"


def test_causal_trace_observes_executed_repository_file(tmp_path):
    package = tmp_path / "pkg"
    package.mkdir()
    (package / "__init__.py").write_text("")
    (package / "target.py").write_text("VALUE = 1\n")
    (tmp_path / "runner.py").write_text("import pkg.target\nassert pkg.target.VALUE == 1\n")
    completed, executed = run_with_causal_trace(
        ["python", "runner.py"],
        repository_root=tmp_path,
        cwd=tmp_path,
        env={},
    )
    assert completed.returncode == 0
    assert "pkg/target.py" in executed


def test_causal_trace_observes_pytest_executed_repository_file(tmp_path):
    package = tmp_path / "pkg"
    package.mkdir()
    (package / "__init__.py").write_text("")
    (package / "target.py").write_text(
        "def value():\n"
        "    return 1\n"
    )
    (tmp_path / "test_target.py").write_text(
        "from pkg.target import value\n"
        "\n"
        "def test_value():\n"
        "    assert value() == 1\n"
    )
    completed, executed = run_with_causal_trace(
        ["python", "-m", "pytest", "-q", "test_target.py"],
        repository_root=tmp_path,
        cwd=tmp_path,
        env={},
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "pkg/target.py" in executed
