from gnosis.evolution.machine_participant import MachineParticipant, ParticipantState
from gnosis.evolution.transfer_authorization import authorize_transfer

def test_active_participant_must_be_in_scope():
    p=MachineParticipant("m1","p1",("Gnozis-V2/research",),state=ParticipantState.ACTIVE)
    assert authorize_transfer(p,"Gnozis-V2/research").authorized
    assert not authorize_transfer(p,"Gnozis-V2/core").authorized

def test_inactive_participant_cannot_transfer_even_if_scoped():
    p=MachineParticipant("m1","p1",("Gnozis-V2/research",),state=ParticipantState.REVOKED)
    assert not authorize_transfer(p,"Gnozis-V2/research").authorized
