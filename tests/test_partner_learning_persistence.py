import pytest
from gnosis.core import Candidate, State, TestResult, TransitionRecord
from gnosis.storage.database import connect
from gnosis.storage.repositories import append_audit
from gnosis.self_learning.partner_transaction import partner_learning_transaction
from gnosis.self_learning.partner_learning_persistence import commit_partner_learning

def fixture():
    conn = connect(":memory:")
    parent = State(elements={"v": 1})
    proposed = parent.with_elements({"v": 2})
    candidate = Candidate(parent.state_id, proposed, "partner:test", 7)
    from gnosis.storage.repositories import save_state, save_candidate
    save_state(conn, parent)
    save_candidate(conn, candidate)
    transition = TransitionRecord(parent.state_id, proposed.state_id, candidate.candidate_id, TestResult(True, ("partner verified",)), True, "committed", "test:partner")
    conn.execute("INSERT INTO instances(instance_id,parent_instance_id,owner_id,root_state_id,current_state_id,generation,status,budget_total,budget_spent,created_at) VALUES(?,?,?,?,?,?,?,?,?,?)", ("inst:1", None, "owner:1", parent.state_id, proposed.state_id, 0, "active", 10, 1, "t"))
    conn.execute("INSERT INTO transitions(transition_id,instance_id,candidate_id,from_state_id,to_state_id,accepted,reasons,test_rule_id,created_at) VALUES(?,?,?,?,?,?,?,?,?)", (transition.transition_id, "inst:1", candidate.candidate_id, parent.state_id, proposed.state_id, 1, '["partner verified"]', "test:partner", "t"))
    return conn, candidate, transition

def kwargs(candidate, transition, request="req:1"):
    return dict(request_id=request, instance_id="inst:1", candidate_id=candidate.candidate_id, transition_id=transition.transition_id, state_id=transition.to_state_id, provenance_digest="prov:1", evidence=("evidence:1",), outcome="accepted", actor="partner:actor")

def test_persists_memory_and_audit():
    conn, candidate, transition = fixture()
    result = commit_partner_learning(conn, **kwargs(candidate, transition))
    assert result.memory_id
    assert conn.execute("SELECT count(*) FROM evolution_memory").fetchone()[0] == 1
    assert conn.execute("SELECT count(*) FROM audit_events WHERE event_id=?", ("partner-learning:req:1",)).fetchone()[0] == 1

def test_exact_replay_is_idempotent():
    conn, candidate, transition = fixture()
    args = kwargs(candidate, transition, "req:replay")
    assert commit_partner_learning(conn, **args) == commit_partner_learning(conn, **args)
    assert conn.execute("SELECT count(*) FROM evolution_memory").fetchone()[0] == 1
    assert conn.execute("SELECT count(*) FROM audit_events WHERE event_id=?", ("partner-learning:req:replay",)).fetchone()[0] == 1

def test_conflicting_replay_fails_closed():
    conn, candidate, transition = fixture()
    args = kwargs(candidate, transition, "req:conflict")
    commit_partner_learning(conn, **args)
    args["provenance_digest"] = "prov:tampered"
    with pytest.raises(Exception):
        commit_partner_learning(conn, **args)
    assert conn.execute("SELECT count(*) FROM evolution_memory").fetchone()[0] == 1
    assert conn.execute("SELECT count(*) FROM audit_events").fetchone()[0] == 1

def test_missing_transition_fails_closed():
    conn, candidate, transition = fixture()
    args = kwargs(candidate, transition, "req:bad")
    args["transition_id"] = "missing"
    with pytest.raises(Exception):
        commit_partner_learning(conn, **args)
    assert conn.execute("SELECT count(*) FROM evolution_memory").fetchone()[0] == 0

def test_transaction_failure_rolls_back():
    conn, candidate, transition = fixture()
    with pytest.raises(RuntimeError):
        with partner_learning_transaction(conn, failure_point="commit"):
            conn.execute("INSERT INTO audit_events(event_id,sequence,actor,action,resource,result,timestamp,prev_hash,event_hash) VALUES(?,?,?,?,?,?,?,?,?)", ("x", 1, "a", "b", "c", "d", "t", "0"*64, "h"))
    assert conn.execute("SELECT count(*) FROM audit_events").fetchone()[0] == 0
