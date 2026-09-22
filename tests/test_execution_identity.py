from gnosis.core.types import TestResult
from gnosis.core.check_identity import check_identity
from gnosis.core.execution_input import execution_input_from_state
from gnosis.core.execution_identity import execution_identity, verify_execution_identity
from gnosis.core.types import State

def test_execution_identity_round_trip():
    check=check_identity("A","check:A",{"predicate":"x>0"})
    result=TestResult(True,("ok",))
    i=execution_identity(check,execution_input_from_state(State({"x":1},(),1),"sandbox"),{"mode":"sandbox"},result)
    assert verify_execution_identity(i,check,execution_input_from_state(State({"x":1},(),1),"sandbox"),{"mode":"sandbox"},result)

def test_input_tamper_detected():
    check=check_identity("A","check:A",{"predicate":"x>0"})
    result=TestResult(True,("ok",))
    i=execution_identity(check,execution_input_from_state(State({"x":1},(),1),"sandbox"),{"mode":"sandbox"},result)
    assert not verify_execution_identity(i,check,execution_input_from_state(State({"x":2},(),1),"sandbox"),{"mode":"sandbox"},result)

def test_context_tamper_detected():
    check=check_identity("A","check:A",{"predicate":"x>0"})
    result=TestResult(True,("ok",))
    i=execution_identity(check,execution_input_from_state(State({"x":1},(),1),"sandbox"),{"mode":"sandbox"},result)
    assert not verify_execution_identity(i,check,execution_input_from_state(State({"x":1},(),1),"commit"),{"mode":"commit"},result)

def test_result_tamper_detected():
    check=check_identity("A","check:A",{"predicate":"x>0"})
    i=execution_identity(check,execution_input_from_state(State({"x":1},(),1),"sandbox"),{"mode":"sandbox"},TestResult(True,("ok",)))
    assert not verify_execution_identity(i,check,execution_input_from_state(State({"x":1},(),1),"sandbox"),{"mode":"sandbox"},TestResult(False,("bad",)))
