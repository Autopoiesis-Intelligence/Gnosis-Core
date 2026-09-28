from pathlib import Path

from gnosis.self_learning.e7_114_runtime_attestation import attest_checkout


def test_runtime_attestation_binds_actual_head(tmp_path, monkeypatch):
    class Result:
        returncode = 0
        stdout = "a" * 40 + "\n"
        stderr = ""

    monkeypatch.setattr(
        "gnosis.self_learning.e7_114_runtime_attestation.subprocess.run",
        lambda *args, **kwargs: Result(),
    )
    result = attest_checkout(Path(tmp_path), "a" * 40)
    assert result.status == "PASS"
    assert result.actual_head_sha == "a" * 40
    assert len(result.evidence_digest) == 64


def test_runtime_attestation_rejects_wrong_head(tmp_path, monkeypatch):
    class Result:
        returncode = 0
        stdout = "b" * 40 + "\n"
        stderr = ""

    monkeypatch.setattr(
        "gnosis.self_learning.e7_114_runtime_attestation.subprocess.run",
        lambda *args, **kwargs: Result(),
    )
    result = attest_checkout(Path(tmp_path), "a" * 40)
    assert result.status == "FAIL"
