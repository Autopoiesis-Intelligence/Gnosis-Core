import pytest
from gnosis.self_learning.specialized_core import create_specialized_core_spec, validate_delivery_scope

def make():
    return create_specialized_core_spec(
        base_core_contract="core-minimal-v1", domain="partner:finance",
        knowledge_scope="partner:finance:knowledge",
        constraint_refs=("constraint:1",), evolution_contract_refs=("E7.62",),
        delivery_revision="r1")

def test_specialized_core_is_proposed():
    assert make().status=="PROPOSED"

def test_scope_is_authorized_explicitly():
    assert validate_delivery_scope(make(),allowed_domains={"partner:finance"}).domain=="partner:finance"

def test_scope_escalation_is_blocked():
    with pytest.raises(PermissionError):
        validate_delivery_scope(make(),allowed_domains={"partner:game"})

def test_identity_is_deterministic():
    assert make()==make()
