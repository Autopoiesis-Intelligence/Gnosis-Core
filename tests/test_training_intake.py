import pytest
from gnosis.self_learning.training_intake import create_training_intake,authorize_training_intake

def make():
    return create_training_intake(partner_id="partner-a",contract_id="sha256:c",domain="finance",knowledge_scope="partner:finance",source_refs=("source:1",),constraints=("constraint:1",),requested_revision="r1")

def test_intake_is_proposed():
    assert make().status=="PROPOSED"

def test_authorized_intake():
    assert authorize_training_intake(make(),allowed_partner_ids={"partner-a"},allowed_scopes={"partner:finance"}).domain=="finance"

def test_wrong_partner_blocked():
    with pytest.raises(PermissionError): authorize_training_intake(make(),allowed_partner_ids={"partner-b"},allowed_scopes={"partner:finance"})

def test_wrong_scope_blocked():
    with pytest.raises(PermissionError): authorize_training_intake(make(),allowed_partner_ids={"partner-a"},allowed_scopes={"partner:game"})
