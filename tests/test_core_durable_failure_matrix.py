import pytest

from gnosis.core import Candidate, State
from gnosis.core.durable_commit import persist_authorized_transition
from gnosis.core.governance import AuthorizationPackage
from gnosis.core.rule_proposal import RuleProposal
from gnosis.instances.instance import Instance
from gnosis.storage import connect, load_instance, save_instance, verify_durable_graph


CHECKPOINTS = [
    "before_begin",
    "after_begin",
    "after_candidate",
    "after_transition",
    "after_audit",
    "after_head",
    "before_commit",
]


def _prepare(path):
    conn = connect(path)
    instance = Instance.create_root("u", State(elements={"root": 0}))
    save_instance(conn, instance)
    old_state_id = instance.engine.state.state_id
    proposed = instance.engine.state.with_elements({"next": 1})
    candidate = Candidate(instance.engine.state.state_id, proposed, "crash-test")
    transition = instance.engine.step(candidate)
    proposal = RuleProposal("rule:x", "gap:x", "finding:x", ("e1",), "supported")
    authorization = AuthorizationPackage(
        "auth:x", proposal.proposal_id, ("e1",), (), "shadow:x", "AUTHORIZED"
    )
    return conn, instance, candidate, transition, proposal, authorization, proposed, old_state_id


@pytest.mark.parametrize("point", CHECKPOINTS)
def test_authorized_core_commit_rolls_back_at_every_precommit_checkpoint(tmp_path, point):
    path = tmp_path / f"{point}.sqlite"
    conn, instance, candidate, transition, proposal, authorization, proposed, old_state_id = _prepare(path)
    with pytest.raises(RuntimeError, match="injected failure"):
        persist_authorized_transition(
            conn, authorization, proposal, instance, candidate, transition,
            actor="core", failure_at=point,
        )
    conn.close()

    reopened = connect(path)
    recovered = load_instance(reopened, instance.instance_id)
    assert recovered.engine.state.state_id == old_state_id
    assert recovered.engine.state.state_id != proposed.state_id
    assert reopened.execute("SELECT COUNT(*) FROM transitions").fetchone()[0] == 0
    assert reopened.execute(
        "SELECT COUNT(*) FROM audit_events WHERE transition_id IS NOT NULL"
    ).fetchone()[0] == 0
    assert verify_durable_graph(reopened)[0] == 1


def test_authorized_core_commit_after_commit_is_durable(tmp_path):
    path = tmp_path / "after-commit.sqlite"
    conn, instance, candidate, transition, proposal, authorization, proposed, _old_state_id = _prepare(path)
    with pytest.raises(RuntimeError, match="injected failure"):
        persist_authorized_transition(
            conn, authorization, proposal, instance, candidate, transition,
            actor="core", failure_at="after_commit",
        )
    conn.close()

    reopened = connect(path)
    recovered = load_instance(reopened, instance.instance_id)
    assert recovered.engine.state.state_id == proposed.state_id
    assert reopened.execute("SELECT COUNT(*) FROM transitions").fetchone()[0] == 1
    assert reopened.execute(
        "SELECT COUNT(*) FROM audit_events WHERE transition_id IS NOT NULL"
    ).fetchone()[0] == 1
    assert verify_durable_graph(reopened)[0] == 2
