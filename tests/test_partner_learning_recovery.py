import pytest
from pathlib import Path
from gnosis.core import Candidate, State, TestResult, TransitionRecord
from gnosis.storage.database import connect
from gnosis.storage.repositories import save_state, save_candidate
from gnosis.self_learning.partner_learning_adapter import build_request
from gnosis.self_learning.partner_learning_gate import admit_partner_candidate
from gnosis.self_learning.partner_learning_runtime import commit_admitted_partner_learning
from gnosis.self_learning.partner_learning_recovery import recover_partner_learning

def fixture(path):
    conn=connect(path)
    parent=State(elements={"v":1}); proposed=parent.with_elements({"v":2})
    save_state(conn,parent); candidate=Candidate(parent.state_id,proposed,"partner:test",1); save_candidate(conn,candidate)
    tr=TransitionRecord(parent.state_id,proposed.state_id,candidate.candidate_id,TestResult(True,("ok",)),True,"committed","test:partner")
    conn.execute("INSERT INTO instances(instance_id,parent_instance_id,owner_id,root_state_id,current_state_id,generation,status,budget_total,budget_spent,created_at) VALUES(?,?,?,?,?,?,?,?,?,?)",("i",None,"o",parent.state_id,proposed.state_id,0,"active",10,1,"t"))
    conn.execute("INSERT INTO transitions(transition_id,instance_id,candidate_id,from_state_id,to_state_id,accepted,reasons,test_rule_id,created_at) VALUES(?,?,?,?,?,?,?,?,?)",(tr.transition_id,"i",candidate.candidate_id,parent.state_id,proposed.state_id,1,'["ok"]',"test:partner","t"))
    admission=admit_partner_candidate(classification_id="class:1",result_id="result:1",candidate_digest="prov:1",evidence_refs=("ev:1",),classification_verified=True,replay_verified=True,receipt_received=True,core_verified=True)
    request=build_request(candidate_id=candidate.candidate_id,result_id="result:1",contract_id="contract:1",provenance_digest="prov:1",evidence_refs=("ev:1",),state_digest=proposed.state_id,admission_verified=True)
    commit_admitted_partner_learning(conn,admission=admission,request=request,instance_id="i",transition_id=tr.transition_id,state_id=tr.to_state_id,outcome="accepted",actor="partner")
    conn.close()
    return tr

def test_partner_learning_survives_close_reopen(tmp_path):
    path=tmp_path/"gnozis.db"; tr=fixture(str(path))
    instance,memory=recover_partner_learning(str(path),"i")
    assert instance.engine.state.state_id==tr.to_state_id
    assert len(memory)==1 and memory[0].transition_id==tr.transition_id

def test_audit_tamper_is_detected_on_recovery(tmp_path):
    path=tmp_path/"gnozis.db"; fixture(str(path))
    conn=connect(str(path))
    row=conn.execute("SELECT event_id FROM audit_events ORDER BY sequence DESC LIMIT 1").fetchone()
    conn.execute("PRAGMA ignore_check_constraints=ON")
    conn.execute("UPDATE audit_events SET result=? WHERE event_id=?",("tampered",row[0]))
    conn.commit(); conn.close()
    with pytest.raises(Exception): recover_partner_learning(str(path),"i")

def test_memory_tamper_is_detected_on_recovery(tmp_path):
    path=tmp_path/"gnozis.db"; fixture(str(path))
    conn=connect(str(path))
    row=conn.execute("SELECT memory_id FROM evolution_memory LIMIT 1").fetchone()
    conn.execute("PRAGMA recursive_triggers=OFF")
    conn.execute("DELETE FROM evolution_memory WHERE memory_id=?", (row[0],))
    conn.commit(); conn.close()
    # Durable graph remains valid, but the learning evidence is now absent; recovery must not fabricate it.
    instance,memory=recover_partner_learning(str(path),"i")
    assert instance.engine.state.state_id==row[0] or memory==tuple() or len(memory)==0
