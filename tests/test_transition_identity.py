from gnosis.core.transition_identity import transition_id, verify_transition_identity
from gnosis.core.types import TransitionRecord, TestResult

def rec():
    return TransitionRecord("s1","s2","c1",TestResult(True,("ok",)),True,"accepted","rule:1")

def test_transition_id_is_content_derived():
    r=rec(); tid=transition_id(r)
    assert tid.startswith("transition:")
    assert verify_transition_identity(r,tid)

def test_transition_identity_rejects_tampering():
    r=rec()
    assert not verify_transition_identity(r,"transition:tampered")

def test_transition_identity_changes_when_record_changes():
    r=rec()
    r2=TransitionRecord("s1","s3","c1",TestResult(True,("ok",)),True,"accepted","rule:1")
    assert transition_id(r)!=transition_id(r2)
