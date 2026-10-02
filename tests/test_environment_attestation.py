from __future__ import annotations

import pytest

from gnosis.self_learning.environment_attestation import (
    create_environment_attestation,
    validate_environment_attestation,
)


def make_attestation():
    return create_environment_attestation(
        scope_lock_id="sha256:scope",
        observed_at="2026-10-02T03:00:00+02:00",
        python_version="3.11.14",
        platform="Linux-6.x-x86_64",
        runtime_identity="runner:proof-01",
        dependency_digest="sha256:deps",
        environment_facts=("git-clean", "network-disabled"),
    )


def test_environment_attestation_is_deterministically_bound_to_scope():
    first = make_attestation()
    second = make_attestation()
    assert first == second
    assert first.attestation_id.startswith("sha256:")


def test_environment_attestation_rejects_scope_substitution():
    attestation = make_attestation()
    with pytest.raises(ValueError, match="scope lock"):
        validate_environment_attestation(
            attestation,
            expected_scope_lock_id="sha256:other",
            actual_python_version="3.11.14",
            actual_platform="Linux-6.x-x86_64",
            actual_runtime_identity="runner:proof-01",
            actual_dependency_digest="sha256:deps",
        )


def test_environment_attestation_rejects_runtime_substitution():
    attestation = make_attestation()
    with pytest.raises(ValueError, match="runtime identity"):
        validate_environment_attestation(
            attestation,
            expected_scope_lock_id="sha256:scope",
            actual_python_version="3.11.14",
            actual_platform="Linux-6.x-x86_64",
            actual_runtime_identity="runner:other",
            actual_dependency_digest="sha256:deps",
        )


def test_environment_attestation_rejects_dependency_substitution():
    attestation = make_attestation()
    with pytest.raises(ValueError, match="dependency digest"):
        validate_environment_attestation(
            attestation,
            expected_scope_lock_id="sha256:scope",
            actual_python_version="3.11.14",
            actual_platform="Linux-6.x-x86_64",
            actual_runtime_identity="runner:proof-01",
            actual_dependency_digest="sha256:other",
        )


def test_environment_attestation_rejects_mutable_status():
    attestation = make_attestation()
    object.__setattr__(attestation, "status", "REVOKED")
    with pytest.raises(ValueError, match="not valid"):
        validate_environment_attestation(
            attestation,
            expected_scope_lock_id="sha256:scope",
            actual_python_version="3.11.14",
            actual_platform="Linux-6.x-x86_64",
            actual_runtime_identity="runner:proof-01",
            actual_dependency_digest="sha256:deps",
        )


def test_environment_attestation_id_changes_when_environment_changes():
    first = make_attestation()
    second = create_environment_attestation(
        scope_lock_id="sha256:scope",
        observed_at="2026-10-02T03:00:00+02:00",
        python_version="3.12.0",
        platform="Linux-6.x-x86_64",
        runtime_identity="runner:proof-01",
        dependency_digest="sha256:deps",
        environment_facts=("git-clean", "network-disabled"),
    )
    assert first.attestation_id != second.attestation_id
