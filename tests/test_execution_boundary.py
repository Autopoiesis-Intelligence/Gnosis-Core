import pytest
from gnosis.self_learning.execution_boundary import authorize_execution,scope_matches,may_execute,creates_new_contract
def make(): return authorize_execution(contract_id="contract:1",contract_digest="sha256:c",scope="partner:a",task_ref="task:1",expected_result="validated core")
def test_accepted_contract_can_be_authorized(): assert make().status=="AUTHORIZED"
def test_identity_and_scope_are_required_for_execution(): assert may_execute(authorization=make(),contract_id="contract:1",contract_digest="sha256:c",scope="partner:a")
def test_wrong_digest_blocks(): assert not may_execute(authorization=make(),contract_id="contract:1",contract_digest="sha256:x",scope="partner:a")
def test_wrong_scope_blocks(): assert not may_execute(authorization=make(),contract_id="contract:1",contract_digest="sha256:c",scope="partner:b")
def test_scope_match(): assert scope_matches(authorization=make(),scope="partner:a")
def test_unaccepted_blocks():
    with pytest.raises(ValueError): authorize_execution(contract_id="c",contract_digest="d",scope="s",task_ref="t",expected_result="e",accepted=False)
def test_no_contract_creation(): assert not creates_new_contract(authorization=make())
def test_deterministic(): assert make()==make()
