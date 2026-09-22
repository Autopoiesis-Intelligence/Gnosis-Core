from gnosis.core.types import State, TestResult
from gnosis.core.check_identity import check_identity
from gnosis.core.execution_input import execution_input_from_state
from gnosis.core.execution_identity import execution_identity, verify_execution_contract

def test_execution_contract_binds_identity_input_and_state():
 state=State({"x":1},(),1); check=check_identity("A","check:A",{"predicate":"x>0"}); result=TestResult(True,("ok",))
 inp=execution_input_from_state(state,"sandbox"); identity=execution_identity(check,inp,{"mode":"sandbox"},result)
 assert verify_execution_contract(identity,check,inp,state,{"mode":"sandbox"},result)

def test_execution_contract_rejects_state_substitution_even_with_matching_shape():
 a=State({"x":1},(),1); b=State({"x":2},(),1); check=check_identity("A","check:A",{"predicate":"x>0"}); result=TestResult(True,("ok",))
 inp=execution_input_from_state(a,"sandbox"); identity=execution_identity(check,inp,{"mode":"sandbox"},result)
 assert not verify_execution_contract(identity,check,inp,b,{"mode":"sandbox"},result)

def test_execution_contract_rejects_tampered_execution_input_digest():
 state=State({"x":1},(),1); check=check_identity("A","check:A",{"predicate":"x>0"}); result=TestResult(True,("ok",))
 inp=execution_input_from_state(state,"sandbox"); identity=execution_identity(check,inp,{"mode":"sandbox"},result)
 tampered=inp.__class__(inp.input_type,inp.state_id,"wrong",inp.content_digest)
 assert not verify_execution_contract(identity,check,tampered,state,{"mode":"sandbox"},result)
