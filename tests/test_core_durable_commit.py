import pytest

from gnosis.core import Candidate, State, TestResult, TransitionRecord
from gnosis.core.durable_commit import persist_authorized_transition
from gnosis.core.governance import AuthorizationPackage
from gnosis.core.rule_proposal import RuleProposal
from gnosis.instances.instance import Instance
from gnosis.storage import connect, recover_instance, save_instance, verify_durable_graph


def _setup():
    conn = connect()
    instance = Instance.create_root("u", State(elements={"a": 1}))
    save_instance(conn, instance)
    proposed = instance.engine.state.with_elements({"b": 2})
    candidate = Candidate(instance.engine.state.state_id, proposed, "autopoiesis")
    transition = instance.engine.step(candidate)
    proposal = RuleProposal("rule:x", "gap:x", "finding:x", ("e1",), "supported")
    authorization = AuthorizationPackage(
        "auth:x", proposal.proposal_id, ("e1",), (), "shadow:x", "AUTHORIZED"
    )
    return conn, instance, candidate, transition, proposal, authorization


def test_authorized_core_commit_uses_existing_durable_transaction():
    conn, instance, candidate, transition, proposal, authorization = _setup()
    record = persist_authorized_transition(
        conn, authorization, proposal, instance, candidate, transition, actor="core"
    )
    assert record.previous_state_id != record.new_state_id
    assert recover_instance(conn, instance.instance_id).engine.state.state_id == record.new_state_id
    assert verify_durable_graph(conn)[0] == 2


def test_durable_adapter_rejects_unauthorized_proposal():
    conn, instance, candidate, transition, proposal, authorization = _setup()
    rejected = AuthorizationPackage(
        "auth:x", proposal.proposal_id, ("e1",), (), "shadow:x", "REJECTED"
    )
    with pytest.raises(ValueError):
        persist_authorized_transition(
            conn, rejected, proposal, instance, candidate, transition, actor="core"
        )
    assert recover_instance(conn, instance.instance_id).engine.state.state_id == transition.from_state_id
    assert verify_durable_graph(conn)[0] == 1


def test_durable_adapter_failure_rolls_back_new_state_and_audit():
    conn, instance, candidate, transition, proposal, authorization = _setup()
    with pytest.raises(RuntimeError, match="injected failure"):
        persist_authorized_transition(
            conn,
            authorization,
            proposal,
            instance,
            candidate,
            transition,
            actor="core",
            failure_at="after_transition",
        )
    assert recover_instance(conn, instance.instance_id).engine.state.state_id == transition.from_state_id
    assert verify_durable_graph(conn)[0] == 1
