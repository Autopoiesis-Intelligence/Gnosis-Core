import pytest
from gnosis.self_learning.collaboration_incident_resolution import create_incident_resolution,resolution_is_learning_safe,resolution_grants_authority

def make(state="UNKNOWN",resolution="CONFIRMED_UNKNOWN"):
    return create_incident_resolution(incident_id="incident:1",evidence_refs=("evidence:1",),conflicting_evidence_refs=("evidence:2",) if state=="CONFLICT" else (),original_scope="public:proposal",observed_scope="public:proposal",incident_state=state,resolution=resolution,rationale="evidence reconciled",resolver_id="reviewer",resolution_revision="r1")

def test_unknown_resolution_is_learning_safe_as_unknown():
    assert resolution_is_learning_safe(record=make())

def test_conflict_requires_conflicting_evidence():
    with pytest.raises(ValueError): make("CONFLICT")

def test_resolution_never_grants_authority():
    assert not resolution_grants_authority(record=make())

def test_scope_mismatch_is_distinct():
    r=make("SCOPE_MISMATCH","SCOPE_MISMATCH_CONFIRMED")
    assert resolution_is_learning_safe(record=r)

def test_deferred_resolution_is_not_learning_safe():
    r=make("UNKNOWN","MANUAL_DEFERRED")
    assert not resolution_is_learning_safe(record=r)

def test_identity_is_deterministic():
    assert make()==make()
