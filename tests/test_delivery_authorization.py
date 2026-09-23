import pytest
from gnosis.self_learning.delivery_authorization import create_delivery_authorization,delivery_authorized,validate_delivery_authorization_binding

def make(status="AUTHORIZED"):
    return create_delivery_authorization(release_gate_id="sha256:gate",build_record_id="sha256:build",delivery_manifest_id="sha256:manifest",partner_id="partner-a",knowledge_scope="partner:finance",authorization_revision="r1",status=status)

def test_authorization_requires_release_and_built_core():
    assert delivery_authorized(release_decision="RELEASE",build_status="BUILT",manifest_status="PROPOSED",authorization=make())

def test_hold_blocks_delivery():
    assert not delivery_authorized(release_decision="HOLD",build_status="BUILT",manifest_status="PROPOSED",authorization=make())

def test_nonbuilt_core_blocks_delivery():
    assert not delivery_authorized(release_decision="RELEASE",build_status="PROPOSED",manifest_status="PROPOSED",authorization=make())

def test_revoked_authorization_blocks_delivery():
    assert not delivery_authorized(release_decision="RELEASE",build_status="BUILT",manifest_status="PROPOSED",authorization=make("REVOKED"))

def test_identity_is_deterministic():
    assert make()==make()


def test_tampered_authorization_identity_is_rejected():
    from dataclasses import replace
    authorization=make()
    with pytest.raises(ValueError,match="authorization identity"):
        validate_delivery_authorization_binding(replace(authorization, partner_id="partner-b"),
            expected_release_gate_id="sha256:gate",expected_build_record_id="sha256:build",expected_delivery_manifest_id="sha256:manifest",expected_partner_id="partner-a",expected_knowledge_scope="partner:finance")

def test_foreign_build_cannot_be_authorized_for_delivery():
    with pytest.raises(PermissionError,match="authorization binding"):
        validate_delivery_authorization_binding(make(),
            expected_release_gate_id="sha256:gate",expected_build_record_id="sha256:foreign-build",expected_delivery_manifest_id="sha256:manifest",expected_partner_id="partner-a",expected_knowledge_scope="partner:finance")
