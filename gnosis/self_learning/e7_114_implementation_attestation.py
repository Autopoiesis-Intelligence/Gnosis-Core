"""E7 attestation of implementation files in the locked checkout."""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

@dataclass(frozen=True)
class ImplementationAttestation:
    path: str
    digest: str

def attest_implementation_paths(repository_root: str | Path, paths: tuple[str, ...]) -> tuple[ImplementationAttestation, ...]:
    root = Path(repository_root).resolve()
    out = []
    for relative in paths:
        p = Path(relative)
        if p.is_absolute() or ".." in p.parts:
            raise RuntimeError(f"implementation path escapes repository: {relative}")
        target = (root / p).resolve()
        if target != root and root not in target.parents:
            raise RuntimeError(f"implementation path escapes repository: {relative}")
        if not target.is_file():
            raise RuntimeError(f"locked implementation file is missing: {relative}")
        out.append(ImplementationAttestation(relative, sha256(target.read_bytes()).hexdigest()))
    if len(out) != len(set(a.path for a in out)):
        raise RuntimeError("duplicate implementation paths are forbidden")
    return tuple(out)

def verify_implementation_attestations(repository_root: str | Path, attestations: tuple[ImplementationAttestation, ...], expected_paths: tuple[str, ...]) -> bool:
    if tuple(a.path for a in attestations) != tuple(expected_paths):
        return False
    try:
        return attest_implementation_paths(repository_root, expected_paths) == attestations
    except RuntimeError:
        return False
