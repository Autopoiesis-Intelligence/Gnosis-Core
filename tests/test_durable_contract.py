import pytest
from gnosis.core.durable_contract import DurableEvolutionContract

def test_contract_requires_all_identities():
    c=DurableEvolutionContract("c1","t1","p1","a1")
    assert c.required_links()[0]==("cycle_id","c1")

def test_contract_rejects_empty_identity():
    with pytest.raises(ValueError):
        DurableEvolutionContract("c1","t1","","a1").validate()

def test_contract_rejects_duplicate_identity():
    with pytest.raises(ValueError):
        DurableEvolutionContract("c1","t1","t1","a1").validate()
