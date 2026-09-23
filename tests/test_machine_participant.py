from gnosis.evolution.machine_participant import MachineParticipant, ParticipantState

def test_pending_cannot_submit():
    p=MachineParticipant("m1","p1",("Gnozis-V2",))
    assert p.state is ParticipantState.PENDING
    assert not p.can_submit_transfer()

def test_active_can_submit():
    p=MachineParticipant("m1","p1",("Gnozis-V2",),state=ParticipantState.ACTIVE)
    assert p.can_submit_transfer()

def test_revocation_is_fail_closed_and_preserves_identity():
    p=MachineParticipant("m1","p1",("Gnozis-V2",),state=ParticipantState.ACTIVE,provenance_id="prov")
    r=p.revoke("2026-09-23T08:00:00Z")
    assert r.state is ParticipantState.REVOKED
    assert not r.can_submit_transfer()
    assert r.machine_id == p.machine_id
    assert r.participant_id == p.participant_id
    assert r.provenance_id == p.provenance_id
    assert r.revoked_at == "2026-09-23T08:00:00Z"

def test_revoke_is_idempotent():
    p=MachineParticipant("m1","p1",("Gnozis-V2",),state=ParticipantState.REVOKED,revoked_at="t")
    assert p.revoke("other") == p
