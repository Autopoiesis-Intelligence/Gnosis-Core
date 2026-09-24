import pytest
from pathlib import Path
from gnosis.core import Candidate, State, TestResult, TransitionRecord
from gnosis.instances.instance import Instance
from gnosis.storage.database import connect
from gnosis.storage.repositories import save_state, _persist_transition, save_candidate, save_instance
from gnosis.self_learning.partner_learning_adapter import build_request
from gnosis.self_learning.partner_learning_gate import admit_partner_candidate
from gnosis.self_learning.partner_learning_runtime import commit_admitted_partner_learning
from gnosis.self_learning.partner_learning_recovery import recover_partner_learning

def fixture(path):
    conn=connect(path)
    parent=State(elements={"v":1}); proposed=parent.with_elements({"v":2})
    save_state(conn,parent); candidate=Candidate(parent.state_id,proposed,"partner:test",1); save_candidate(conn,candidate)
    tr=TransitionRecord(parent.state_id,proposed.state_id,candidate.candidate_id,TestResult(True,("ok",)),True,"committed","test:partner")
    instance=Instance.create_root("o", parent)
    save_instance(conn, instance)
    instance_id=instance.instance_id
    _persist_transition(conn, instance, candidate, tr, actor="test")
    admission=admit_partner_candidate(classification_id="class:1",result_id="result:1",candidate_digest="prov:1",evidence_refs=("ev:1",),classification_verified=True,replay_verified=True,receipt_received=True,core_verified=True)
    request=build_request(candidate_id=candidate.candidate_id,result_id="result:1",contract_id="contract:1",provenance_digest="prov:1",evidence_refs=("ev:1",),state_digest=proposed.state_id,admission_verified=True)
    commit_admitted_partner_learning(conn,admission=admission,request=request,instance_id=instance_id,transition_id=tr.transition_id,state_id=tr.to_state_id,outcome="accepted",actor="partner")
    conn.close()
    return tr, instance_id

def test_partner_learning_survives_close_reopen(tmp_path):
    path=tmp_path/"gnozis.db"; tr,instance_id=fixture(str(path))
    instance,memory=recover_partner_learning(str(path),instance_id)
    assert instance.engine.state.state_id==tr.to_state_id
    assert len(memory)==1 and memory[0].transition_id==tr.transition_id

def test_audit_tamper_is_detected_on_recovery(tmp_path):
    path=tmp_path/"gnozis.db"; tr,instance_id=fixture(str(path))
    conn=connect(str(path))
    row=conn.execute("SELECT event_id FROM audit_events ORDER BY sequence DESC LIMIT 1").fetchone()
    conn.execute("DROP TRIGGER audit_events_no_update")
    conn.execute("UPDATE audit_events SET result=? WHERE event_id=?",("tampered",row[0]))
    conn.commit(); conn.close()
    with pytest.raises(Exception): recover_partner_learning(str(path),instance_id)

def test_memory_tamper_is_detected_on_recovery(tmp_path):
    path=tmp_path/"gnozis.db"; tr,instance_id=fixture(str(path))
    conn=connect(str(path))
    row=conn.execute("SELECT memory_id FROM evolution_memory LIMIT 1").fetchone()
    conn.execute("DROP TRIGGER evolution_memory_no_update")
    conn.execute("DROP TRIGGER evolution_memory_no_delete")
    conn.execute("UPDATE evolution_memory SET evidence=? WHERE memory_id=?", ('["tampered"]', row[0]))
    conn.commit(); conn.close()
    with pytest.raises(Exception): recover_partner_learning(str(path),instance_id)
