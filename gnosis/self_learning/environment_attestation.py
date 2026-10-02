"""Immutable runtime environment attestation for governed execution.

E7.115 records the execution environment observed immediately before a
governed task. It describes environment state; it grants no authority.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Iterable


@dataclass(frozen=True)
class EnvironmentAttestation:
    attestation_id: str
    scope_lock_id: str
    observed_at: str
    python_version: str
    platform: str
    runtime_identity: str
    dependency_digest: str
    environment_facts: tuple[str, ...]
    status: str = "ATTESTED"
    revision: int = 1

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def create_environment_attestation(
    *,
    scope_lock_id: str,
    observed_at: str,
    python_version: str,
    platform: str,
    runtime_identity: str,
    dependency_digest: str,
    environment_facts: Iterable[str],
) -> EnvironmentAttestation:
    facts = tuple(environment_facts)
    if not all((scope_lock_id, observed_at, python_version, platform, runtime_identity, dependency_digest)):
        raise ValueError("all environment attestation identity fields are required")
    if not facts:
        raise ValueError("environment_facts must not be empty")
    values = {
        "scope_lock_id": scope_lock_id,
        "observed_at": observed_at,
        "python_version": python_version,
        "platform": platform,
        "runtime_identity": runtime_identity,
        "dependency_digest": dependency_digest,
        "environment_facts": facts,
    }
    canonical = json.dumps(values, sort_keys=True, separators=(",", ":"))
    return EnvironmentAttestation(
        attestation_id="sha256:" + hashlib.sha256(canonical.encode()).hexdigest(),
        **values,
    )


def validate_environment_attestation(
    attestation: EnvironmentAttestation,
    *,
    expected_scope_lock_id: str,
    actual_python_version: str,
    actual_platform: str,
    actual_runtime_identity: str,
    actual_dependency_digest: str,
) -> None:
    if attestation.status != "ATTESTED":
        raise ValueError("environment attestation is not valid")
    if attestation.scope_lock_id != expected_scope_lock_id:
        raise ValueError("environment attestation scope lock does not match")
    if attestation.python_version != actual_python_version:
        raise ValueError("environment attestation python version does not match")
    if attestation.platform != actual_platform:
        raise ValueError("environment attestation platform does not match")
    if attestation.runtime_identity != actual_runtime_identity:
        raise ValueError("environment attestation runtime identity does not match")
    if attestation.dependency_digest != actual_dependency_digest:
        raise ValueError("environment attestation dependency digest does not match")


def serialize_environment_attestation(attestation: EnvironmentAttestation) -> str:
    return json.dumps(attestation.as_dict(), sort_keys=True, separators=(",", ":"))
