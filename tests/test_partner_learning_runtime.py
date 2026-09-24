import pytest
from gnosis.core import Candidate, State, TestResult, TransitionRecord
from gnosis.storage.database import connect
from gnosis.storage.repositories import save_state, save_candidate
from gnosis.self_learning.partner_learning_adapter import build_request
from gnosis.self_learning.partner_learning_gate import admit_partner_candidate
from gnosis.self_learning.partner_learning_persistence import commit_partner_learning
from gnosis.self_learning.partner_learning_runtime import commit_admitted_partner_learning

def fixture():
    conn=connect(":memory:")
    parent=State(elements={"v":1}); proposed=parent.with_elements({"v":2})
    save_state(conn,parent); candidate=Candidate(parent.state_id,proposed,"partner:test",1); save_candidate(conn,candidate)
    tr=TransitionRecord(parent.state_id,proposed.state_id,candidate.candidate_id,TestResult(True,("ok",)),True,"committed","test:partner")
    conn.execute("INSERT INTO instances(instance_id,parent_instance_id,owner_id,root_state_id,current_state_id,generation,status,budget_total,budget_spent,created_at) VALUES(?,?,?,?,?,?,?,?,?,?)",("i",None,"o",parent.state_id,proposed.state_id,0,"active",10,1,"t"))
    conn.execute("INSERT INTO transitions(transition_id,instance_id,candidate_id,from_state_id,to_state_id,accepted,reasons,test_rule_id,created_at) VALUES(?,?,?,?,?,?,?,?,?)",(tr.transition_id,"i",candidate.candidate_id,parent.state_id,proposed.state_id,1,'["ok"]',"test:partner","t"))
    admission=admit_partner_candidate(classification_id="class:1",result_id="result:1",candidate_digest="prov:1",evidence_refs=("ev:1",),classification_verified=True,replay_verified=True,receipt_received=True,core_verified=True)
    request=build_request(candidate_id=candidate.candidate_id,result_id="result:1",contract_id="contract:1",provenance_digest="prov:1",evidence_refs=("ev:1",),state_digest=proposed.state_id,admission_verified=True)
    return conn,tr,admission,request

def test_runtime_bridge_persists_only_after_admission():
    conn,tr,admission,request=fixture()
    result=commit_admitted_partner_learning(conn,admission=admission,request=request,instance_id="i",transition_id=tr.transition_id,state_id=tr.to_state_id,outcome="accepted",actor="partner")
    assert result.memory_id
    assert conn.execute("SELECT count(*) FROM evolution_memory").fetchone()[0]==1

def test_binding_mismatch_fails_closed():
    conn,tr,admission,request=fixture()
    bad=build_request(candidate_id=request.candidate_id,result_id="other",contract_id=request.contract_id,provenance_digest=request.provenance_digest,evidence_refs=request.evidence_refs,state_digest=request.state_digest,admission_verified=True)
    with pytest.raises(ValueError):
        commit_admitted_partner_learning(conn,admission=admission,request=bad,instance_id="i",transition_id=tr.transition_id,state_id=tr.to_state_id,outcome="accepted",actor="partner")

def test_unverified_admission_fails_closed():
    conn,tr,admission,request=fixture()
    from gnosis.self_learning.partner_learning_gate import LearningAdmission
    blocked=LearningAdmission(admission.admission_id,admission.classification_id,admission.result_id,admission.candidate_digest,admission.evidence_refs,"ADMITTED",False)
    with pytest.raises(ValueError):
        commit_admitted_partner_learning(conn,admission=blocked,request=request,instance_id="i",transition_id=tr.transition_id,state_id=tr.to_state_id,outcome="accepted",actor="partner")
