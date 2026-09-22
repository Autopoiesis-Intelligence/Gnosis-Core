import sqlite3
import pytest
from gnosis.core import Candidate, State
from gnosis.instances.instance import Instance
from gnosis.storage import append_evolution_memory, connect, load_evolution_memory, save_instance


def test_evolution_memory_round_trip_and_digest():
    conn=connect(); instance=Instance.create_root("u", State(elements={"a":1})); save_instance(conn,instance)
    proposed=instance.engine.state.with_elements({"b":2}); candidate=Candidate(instance.engine.state.state_id,proposed,"reflection:endogenous")
    record=instance.engine.step(candidate)
    from gnosis.storage.repositories import persist_transition
    persist_transition(conn,instance,candidate,record,actor="test")
    tid=conn.execute("SELECT transition_id FROM transitions WHERE candidate_id=?",(candidate.candidate_id,)).fetchone()[0]
    mem=append_evolution_memory(conn,instance_id=instance.instance_id,candidate_id=candidate.candidate_id,transition_id=tid,state_id=proposed.state_id,proposal_id="proposal:1",outcome="accepted",evidence=("finding:1","observation:1"))
    loaded=load_evolution_memory(conn,instance.instance_id)
    assert loaded==(mem,)
    assert mem.digest==mem.memory_id


def test_evolution_memory_is_append_only():
    conn=connect(); instance=Instance.create_root("u", State(elements={"a":1})); save_instance(conn,instance)
    proposed=instance.engine.state.with_elements({"b":2}); candidate=Candidate(instance.engine.state.state_id,proposed,"test")
    record=instance.engine.step(candidate)
    from gnosis.storage.repositories import persist_transition
    persist_transition(conn,instance,candidate,record,actor="test")
    tid=conn.execute("SELECT transition_id FROM transitions WHERE candidate_id=?",(candidate.candidate_id,)).fetchone()[0]
    append_evolution_memory(conn,instance_id=instance.instance_id,candidate_id=candidate.candidate_id,transition_id=tid,state_id=proposed.state_id,proposal_id=None,outcome="rejected",evidence=("rejected",))
    with pytest.raises(sqlite3.DatabaseError): conn.execute("DELETE FROM evolution_memory")
    with pytest.raises(sqlite3.DatabaseError): conn.execute("UPDATE evolution_memory SET outcome='accepted'")


def test_evolution_memory_rejects_unknown_outcome():
    conn=connect()
    with pytest.raises(ValueError): append_evolution_memory(conn,instance_id="i",candidate_id="c",transition_id="t",state_id="s",proposal_id=None,outcome="accepted-ish",evidence=())


def test_evolution_memory_cannot_lie_about_persisted_transition():
    conn=connect(); instance=Instance.create_root("u", State(elements={"a":1})); save_instance(conn,instance)
    proposed=instance.engine.state.with_elements({"b":2}); candidate=Candidate(instance.engine.state.state_id,proposed,"memory-binding")
    record=instance.engine.step(candidate)
    from gnosis.storage.repositories import persist_transition
    persist_transition(conn,instance,candidate,record,actor="test")
    tid=conn.execute("SELECT transition_id FROM transitions WHERE candidate_id=?",(candidate.candidate_id,)).fetchone()[0]

    with pytest.raises(Exception, match="outcome disagrees"):
        append_evolution_memory(conn,instance_id=instance.instance_id,candidate_id=candidate.candidate_id,
            transition_id=tid,state_id=proposed.state_id,proposal_id=None,outcome="rejected",evidence=("false",))

    with pytest.raises(Exception, match="state mismatch"):
        append_evolution_memory(conn,instance_id=instance.instance_id,candidate_id=candidate.candidate_id,
            transition_id=tid,state_id=instance.engine.state.state_id,proposal_id=None,outcome="accepted",evidence=("false",))


def test_load_evolution_memory_rechecks_transition_semantics_after_tamper():
    conn=connect(); instance=Instance.create_root("u", State(elements={"a":1})); save_instance(conn,instance)
    proposed=instance.engine.state.with_elements({"b":2}); candidate=Candidate(instance.engine.state.state_id,proposed,"read-binding")
    record=instance.engine.step(candidate)
    persist_transition(conn,instance,candidate,record,actor="test")
    tid=conn.execute("SELECT transition_id FROM transitions WHERE candidate_id=?",(candidate.candidate_id,)).fetchone()[0]
    mem=append_evolution_memory(conn,instance_id=instance.instance_id,candidate_id=candidate.candidate_id,
        transition_id=tid,state_id=proposed.state_id,proposal_id=None,outcome="accepted",evidence=("ok",))

    conn.execute("UPDATE transitions SET accepted=0 WHERE transition_id=?",(tid,))
    with pytest.raises(Exception, match="outcome disagrees"):
        load_evolution_memory(conn,instance.instance_id)

    conn.execute("UPDATE transitions SET accepted=1,to_state_id=? WHERE transition_id=?",
                 (instance.engine.state.state_id,tid))
    with pytest.raises(Exception, match="state mismatch"):
        load_evolution_memory(conn,instance.instance_id)


def test_evolution_memory_rejects_cross_instance_transition_rebinding():
    conn=connect()
    a=Instance.create_root("a", State(elements={"a":1}))
    b=Instance.create_root("b", State(elements={"b":1}))
    save_instance(conn,a); save_instance(conn,b)
    proposed=a.engine.state.with_elements({"x":2})
    candidate=Candidate(a.engine.state.state_id,proposed,"cross-instance")
    record=a.engine.step(candidate)
    from gnosis.storage.repositories import persist_transition
    persist_transition(conn,a,candidate,record,actor="test")
    tid=conn.execute("SELECT transition_id FROM transitions WHERE candidate_id=?",(candidate.candidate_id,)).fetchone()[0]
    mem=append_evolution_memory(conn,instance_id=a.instance_id,candidate_id=candidate.candidate_id,
        transition_id=tid,state_id=proposed.state_id,proposal_id=None,outcome="accepted",evidence=("ok",))
    raw={"instance_id":b.instance_id,"candidate_id":mem.candidate_id,"transition_id":mem.transition_id,
         "state_id":mem.state_id,"proposal_id":mem.proposal_id,"outcome":mem.outcome,
         "evidence":mem.evidence,"created_at":mem.created_at}
    new_id=__import__("hashlib").sha256(__import__("gnosis.storage.repositories",fromlist=["canonical_json"]).canonical_json(raw).encode()).hexdigest()
    conn.execute("UPDATE evolution_memory SET instance_id=?, memory_id=? WHERE memory_id=?",
                 (b.instance_id,new_id,mem.memory_id))
    with pytest.raises(Exception, match="transition identity mismatch"):
        load_evolution_memory(conn,b.instance_id)


def test_evolution_memory_rejects_tampered_transition_identity_on_reload():
    conn = connect()
    instance = Instance.create_root("u", State(elements={"a": 1}))
    save_instance(conn, instance)
    candidate, record = _transition(instance, "next")
    append_evolution_memory(
        conn, instance_id=instance.instance_id, candidate_id=candidate.candidate_id,
        transition_id=record.transition_id, state_id=record.to_state_id,
        proposal_id=None, outcome="accepted", evidence=("ok",),
    )
    conn.execute("UPDATE transitions SET test_rule_id=? WHERE transition_id=?", ("tampered", record.transition_id))
    with pytest.raises(StorageCorruptionError, match="transition identity mismatch"):
        load_evolution_memory(conn, instance.instance_id)
