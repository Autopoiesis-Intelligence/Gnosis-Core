import pytest
from gnosis.self_learning.partner_learning_runtime import commit_admitted_partner_learning
from tests.test_partner_learning_runtime import fixture

def test_runtime_bridge_rejects_noop_before_durable_commit():
    conn,tr,admission,request=fixture()
    with pytest.raises(ValueError, match="no-op"):
        commit_admitted_partner_learning(
            conn, admission=admission, request=request, instance_id="i",
            transition_id=tr.transition_id, state_id=tr.to_state_id,
            outcome="accepted", actor="partner",
            parent_state_digest=request.state_digest,
        )
    assert conn.execute("SELECT count(*) FROM evolution_memory").fetchone()[0] == 0
