from gnosis.core.types import State
from gnosis.core.execution_input import execution_input_from_state, verify_execution_input

def test_execution_input_round_trip():
    s=State({"x":1},(),1)
    i=execution_input_from_state(s)
    assert verify_execution_input(i,s)

def test_state_substitution_detected():
    a=State({"x":1},(),1); b=State({"x":2},(),1)
    i=execution_input_from_state(a)
    assert not verify_execution_input(i,b)

def test_context_type_is_bound():
    s=State({"x":1},(),1)
    i=execution_input_from_state(s,"sandbox")
    assert verify_execution_input(i,s,"sandbox")
    assert not verify_execution_input(i,s,"commit")
