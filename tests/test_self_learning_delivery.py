import pytest
from gnosis.self_learning.delivery import create_delivery_manifest, authorize_delivery, validate_delivery_build_binding

def make():
    return create_delivery_manifest(
        core_id="sha256:core",
        contract_refs=("E7.62",), knowledge_scope="partner:finance",
        evidence_refs=("sha256:evidence",),
        excluded_components=("private-core-source","other-partner-data"),
        revision="r1")

def test_manifest_is_proposed_and_explicit():
    m=make()
    assert m.status=="PROPOSED"
    assert "private-core-source" in m.excluded_components

def test_delivery_scope_requires_authorization():
    assert authorize_delivery(make(),allowed_scopes={"partner:finance"}).knowledge_scope=="partner:finance"

def test_unauthorized_delivery_is_blocked():
    with pytest.raises(PermissionError):
        authorize_delivery(make(),allowed_scopes={"partner:game"})

def test_manifest_identity_is_deterministic():
    assert make()==make()


def test_tampered_delivery_manifest_identity_is_rejected():
    from dataclasses import replace
    tampered=replace(make(), package_id="sha256:forged")
    with pytest.raises(ValueError, match="delivery manifest identity"):
        authorize_delivery(tampered, allowed_scopes={"partner:finance"})


def test_delivery_cannot_reference_foreign_core():
    manifest=create_delivery_manifest(core_id="sha256:core-a",contract_refs=("E7.68",),knowledge_scope="partner:core",evidence_refs=("ci:pass",),excluded_components=("secrets",),revision="r1")
    with pytest.raises(PermissionError,match="delivery core identity"):
        validate_delivery_build_binding(manifest,expected_core_id="sha256:core-b")
