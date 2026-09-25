import pytest

from registry.core_handoff import create_handoff
from registry.federation_core_adapter import bind_handoff_to_core, core_identity_fields


def make():
    return create_handoff(
        {"result": "AUTHORIZED", "authorization_sha256": "a" * 64},
        {"candidate_id": "c1", "source_id": "s1", "resource_id": "r1"},
        "core-evolution",
        "propose",
        ["e1"],
    )["handoff"]


def test_adapter_accepts_verified_handoff():
    binding = bind_handoff_to_core(make())
    assert binding.handoff_sha256
    assert binding.candidate_id == "c1"


def test_adapter_rejects_tampered_handoff():
    handoff = make()
    handoff["candidate_id"] = "forged"
    with pytest.raises(PermissionError):
        bind_handoff_to_core(handoff)


def test_adapter_exposes_identity_not_authority():
    fields = core_identity_fields(bind_handoff_to_core(make()))
    assert "commit" not in fields
    assert "mutation_capability" not in fields
    assert "authorization" not in fields
    assert fields["candidate_id"] == "c1"
