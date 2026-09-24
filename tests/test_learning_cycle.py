import pytest
from gnosis.self_learning.learning_cycle import start_cycle,provenance_continuous,may_extract,creates_execution_authority
def make(status="STARTED",memory="ADMITTED",parent="sha256:state"):
    return start_cycle(parent_memory_entry_id="memory:1",parent_state_digest=parent,input_refs=("input:1",),scope="self_learning",status=status,memory_status=memory)
def test_admitted_memory_starts_cycle(): assert may_extract(cycle=make())
def test_unadmitted_memory_is_rejected():
    with pytest.raises(ValueError): make(memory="PROPOSED")
def test_provenance_is_bound(): assert provenance_continuous(cycle=make(),parent_memory_entry_id="memory:1",parent_state_digest="sha256:state")
def test_state_or_memory_mismatch_breaks_provenance(): assert not provenance_continuous(cycle=make(),parent_memory_entry_id="memory:other",parent_state_digest="sha256:state"); assert not provenance_continuous(cycle=make(),parent_memory_entry_id="memory:1",parent_state_digest="sha256:other")
def test_completed_cycle_does_not_extract(): assert not may_extract(cycle=make("COMPLETED"))
def test_cycle_never_grants_authority(): assert not creates_execution_authority(cycle=make())
def test_deterministic(): assert make()==make()
