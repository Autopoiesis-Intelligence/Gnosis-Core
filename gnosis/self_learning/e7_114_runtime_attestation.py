"""E7.114 runtime environment attestation."""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import subprocess


@dataclass(frozen=True)
class RuntimeAttestation:
    repository_root: str
    actual_head_sha: str
    expected_commit_sha: str
    status: str
    evidence_digest: str


def attest_checkout(repository_root: str | Path, expected_commit_sha: str) -> RuntimeAttestation:
    root = Path(repository_root).resolve()
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
        actual = result.stdout.strip().lower() if result.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        actual = ""

    status = "PASS" if actual and actual == expected_commit_sha.lower() else "FAIL"
    payload = {
        "repository_root": str(root),
        "actual_head_sha": actual,
        "expected_commit_sha": expected_commit_sha.lower(),
        "status": status,
    }
    digest = sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return RuntimeAttestation(
        repository_root=str(root),
        actual_head_sha=actual,
        expected_commit_sha=expected_commit_sha.lower(),
        status=status,
        evidence_digest=digest,
    )


def assert_attestation_ready(attestation: RuntimeAttestation) -> None:
    if attestation.status != "PASS":
        raise RuntimeError("runtime checkout attestation failed")
