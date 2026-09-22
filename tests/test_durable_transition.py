from gnosis.core.durable_transition import DurableTransition
from gnosis.core.types import TransitionRecord, TestResult
from gnosis.core.transition_identity import transition_id

def test_durable_transition_requires_identity():
    r=TransitionRecord("s1","s2","c1",TestResult(True,("ok",)),True,"accepted")
    DurableTransition(transition_id(r),r,"p1","a1","e1").validate()

def test_durable_transition_rejects_missing_identity():
    import pytest
    r=TransitionRecord("s1","s2","c1",TestResult(True,("ok",)),True,"accepted")
    with pytest.raises(ValueError):
        DurableTransition("transition:c1",r,"","a1","e1").validate()
