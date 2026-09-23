import pytest
from gnosis.self_learning.delivery_receipt import create_delivery_receipt,delivery_receipt_valid,validate_delivery_receipt_binding

def make(status="RECORDED"):
    return create_delivery_receipt(authorization_id="sha256:auth",delivery_manifest_id="sha256:manifest",core_build_revision="core:r1",partner_id="partner-a",knowledge_scope="partner:finance",delivered_revision="delivery:r1",evidence_refs=("transfer:1",),status=status)

def test_valid_receipt_closes_delivery_provenance():
    assert delivery_receipt_valid(authorization_status="AUTHORIZED",release_decision="RELEASE",receipt=make())

def test_unauthorized_delivery_is_invalid():
    assert not delivery_receipt_valid(authorization_status="HOLD",release_decision="RELEASE",receipt=make())

def test_nonreleased_core_is_invalid():
    assert not delivery_receipt_valid(authorization_status="AUTHORIZED",release_decision="HOLD",receipt=make())

def test_rejected_receipt_is_invalid():
    assert not delivery_receipt_valid(authorization_status="AUTHORIZED",release_decision="RELEASE",receipt=make("REJECTED"))

def test_identity_is_deterministic():
    assert make()==make()


def test_tampered_receipt_identity_is_rejected():
    from dataclasses import replace
    receipt=make()
    with pytest.raises(ValueError,match="receipt identity"):
        validate_delivery_receipt_binding(replace(receipt, partner_id="partner-b"),
            expected_authorization_id="sha256:auth",expected_delivery_manifest_id="sha256:manifest",expected_core_build_revision="core:r1",expected_partner_id="partner-a",expected_knowledge_scope="partner:finance")

def test_foreign_authorization_cannot_produce_valid_receipt():
    with pytest.raises(PermissionError,match="receipt binding"):
        validate_delivery_receipt_binding(make(),
            expected_authorization_id="sha256:foreign-auth",expected_delivery_manifest_id="sha256:manifest",expected_core_build_revision="core:r1",expected_partner_id="partner-a",expected_knowledge_scope="partner:finance")
