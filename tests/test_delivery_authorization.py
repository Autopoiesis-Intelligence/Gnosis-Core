import pytest
from gnosis.self_learning.delivery_authorization import create_delivery_authorization,delivery_authorized

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
