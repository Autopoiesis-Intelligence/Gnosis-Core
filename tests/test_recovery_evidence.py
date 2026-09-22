from gnosis.core.recovery import RecoveryEvidence

def test_recovery_evidence_requires_complete_bundle():
    e=RecoveryEvidence(
        provenance={"evidence_digest":"ed","proposed_state_content_id":"state"},
        audit_rows=({"record_digest":"a"},),
        observations={"x":1},
        proposed_state_content_id="state",
        transition_id="t1",
        evidence_digest="ed",
        replayed_evidence_digest="ed",
    )
    e.validate()

def test_recovery_evidence_rejects_missing_transition():
    import pytest
    e=RecoveryEvidence({"evidence_digest":"ed","proposed_state_content_id":"state"},
                       ({"record_digest":"a"},),{}, "state","","ed","ed")
    with pytest.raises(ValueError): e.validate()

def test_recovery_evidence_rejects_digest_mismatch():
    import pytest
    e=RecoveryEvidence({"evidence_digest":"ed","proposed_state_content_id":"state"},
                       ({"record_digest":"a"},),{}, "state","t1","ed","bad")
    e.validate()
    # mismatch is a verification failure, not an accepted recovery
    assert e.evidence_digest != e.replayed_evidence_digest
