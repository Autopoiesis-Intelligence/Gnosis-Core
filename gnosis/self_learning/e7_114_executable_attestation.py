"""E7 runtime executable identity attestation."""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import os
from pathlib import Path
import shutil


@dataclass(frozen=True)
class ExecutableAttestation:
    argv0: str
    resolved_path: str
    digest: str


def attest_executable(argv0: str) -> ExecutableAttestation:
    resolved = shutil.which(argv0, path=os.environ.get("PATH"))
    if not resolved:
        raise RuntimeError(f"locked executable is not resolvable: {argv0}")
    path = Path(resolved).resolve()
    if not path.is_file():
        raise RuntimeError("resolved executable is not a regular file")
    return ExecutableAttestation(argv0=argv0, resolved_path=str(path), digest=sha256(path.read_bytes()).hexdigest())


def verify_executable_attestation(attestation: ExecutableAttestation) -> bool:
    path = Path(attestation.resolved_path)
    if not path.is_file():
        return False
    return sha256(path.read_bytes()).hexdigest() == attestation.digest
