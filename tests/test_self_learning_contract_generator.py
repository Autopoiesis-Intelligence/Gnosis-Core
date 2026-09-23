import pytest
from gnosis.self_learning.contracts import generate_candidate_contract, reject_private_sources

def make():
    return generate_candidate_contract(
        title="Partner learning contract", objective="Validate a bounded domain", scope="partner:demo",
        source_refs=("E7.53",), source_revisions=("r1",), generator_context="self-learning:v1",
        generated_revision="r1", validation_requirements=("evidence","governance")
    )

def test_generated_contract_is_proposed():
    c=make()
    assert c.status=="PROPOSED"
    assert c.authority=="candidate-contract-only"
    assert c.contract_id.startswith("sha256:")

def test_private_scope_is_blocked_without_authorization():
    with pytest.raises(PermissionError):
        reject_private_sources(make(),authorized_scopes={"common-self-learning"})

def test_authorized_partner_scope_is_preserved():
    c=reject_private_sources(make(),authorized_scopes={"partner:demo"})
    assert c.scope=="partner:demo"

def test_generation_is_deterministic():
    assert make()==make()
