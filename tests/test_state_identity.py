import pytest
from gnosis.core.types import State, Relation
from gnosis.core.state_identity import state_digest, state_from_payload, verify_state_digest, canonical_state_payload

def test_state_digest_round_trip():
    s=State({"a":1},(Relation("a","b","r",{"x":[1,2]}),),2)
    assert verify_state_digest(state_from_payload(canonical_state_payload(s)),state_digest(s))

def test_state_digest_detects_content_tamper():
    s=State({"a":1},(),1)
    payload=canonical_state_payload(s); payload["elements"] = {"a": 2}
    restored=state_from_payload(payload)
    assert state_digest(restored)!=state_digest(s)

def test_state_digest_changes_with_version():
    assert state_digest(State({"a":1},(),1))!=state_digest(State({"a":1},(),2))
