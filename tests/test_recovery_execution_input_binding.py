from gnosis.evolution.recovery import recover_evolution_audit
from gnosis.core.types import State

def test_recovery_rejects_parent_state_substitution(db_conn, valid_provenance_fixture):
    provenance_id, observations, proposed_state, parent_state = valid_provenance_fixture
    other = State({"substituted": True}, (), parent_state.version)
    report = recover_evolution_audit(db_conn, provenance_id=provenance_id, observations=observations, proposed_state=proposed_state, parent_state=other)
    assert not report.replay_valid
    assert "recovery execution input binding mismatch" in report.reasons
