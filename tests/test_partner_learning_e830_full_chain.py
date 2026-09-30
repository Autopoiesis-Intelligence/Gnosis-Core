import pytest
from gnosis.core import Candidate, State, TestResult, TransitionRecord
from gnosis.instances.instance import Instance
from gnosis.storage import RecoveryAuthorization, recovery_evidence_digest
from gnosis.storage.database import connect
from gnosis.storage.repositories import save_state, _persist_transition, save_candidate, save_instance, verify_durable_graph, load_state
from gnosis.self_learning.partner_learning_adapter import build_request
from gnosis.self_learning.partner_learning_gate import admit_partner_candidate
from gnosis.self_learning.partner_learning_runtime import commit_admitted_partner_learning
from gnosis.self_learning.partner_learning_recovery import recover_partner_learning


def recovery_auth(path, instance_id):
    conn = connect(path)
    try:
        digest = recovery_evidence_digest(conn, instance_id)
    finally:
        conn.close()
    return RecoveryAuthorization(
        authorization_id="test-recovery", subject=instance_id,
        requested_by="test-principal", authority="test-governance",
        decision="allow", reason="test recovery",
        issued_at="2026-09-25T00:00:00Z", expires_at="2026-09-26T00:00:00Z",
        evidence_digest=digest,
    )

def build_chain(path):
    conn=connect(path); parent=State(elements={"v":1}); proposed=parent.with_elements({"v":2})
    save_state(conn,parent); candidate=Candidate(parent.state_id,proposed,"partner:test",1); save_candidate(conn,candidate)
    tr=TransitionRecord(parent.state_id,proposed.state_id,candidate.candidate_id,TestResult(True,("ok",)),True,"committed","test:partner")
    instance=Instance.create_root("o", parent)
    save_instance(conn, instance)
    instance_id=instance.instance_id
    _persist_transition(conn, instance, candidate, tr, actor="test")
    admission=admit_partner_candidate(classification_id="class:1",result_id="result:1",candidate_digest="prov:1",evidence_refs=("ev:1",),classification_verified=True,replay_verified=True,receipt_received=True,core_verified=True)
    request=build_request(candidate_id=candidate.candidate_id,result_id="result:1",contract_id="contract:1",provenance_digest="prov:1",evidence_refs=("ev:1",),state_digest=proposed.state_id,admission_verified=True)
    result=commit_admitted_partner_learning(conn,admission=admission,request=request,instance_id=instance_id,transition_id=tr.transition_id,state_id=tr.to_state_id,outcome="accepted",actor="partner")
    conn.close(); return tr,result,instance_id

def test_full_chain_survives_reopen(tmp_path):
    path=tmp_path/"g.db"; tr,result,instance_id=build_chain(str(path))
    instance,memory=recover_partner_learning(str(path), instance_id, authorization=recovery_auth(str(path), instance_id), now="2026-09-25T12:00:00Z")
    assert instance.engine.state.state_id==tr.to_state_id
    assert len(memory)==1 and memory[0].memory_id==result.memory_id

@pytest.mark.parametrize("mutation",["audit_result","memory_evidence","transition_candidate","transition_state"])
def test_full_chain_tamper_matrix_fails_closed(tmp_path,mutation):
    path=tmp_path/f"{mutation}.db"; tr,result,instance_id=build_chain(str(path)); conn=connect(str(path))
    if mutation=="audit_result":
        conn.execute("DROP TRIGGER audit_events_no_update"); row=conn.execute("SELECT event_id FROM audit_events WHERE event_id LIKE 'partner-learning:%'").fetchone(); conn.execute("UPDATE audit_events SET result=? WHERE event_id=?",("tamper",row[0]))
    elif mutation=="memory_evidence":
        conn.execute("DROP TRIGGER evolution_memory_no_update");
        conn.execute("DROP TRIGGER evolution_memory_no_delete"); row=conn.execute("SELECT memory_id FROM evolution_memory LIMIT 1").fetchone(); conn.execute("UPDATE evolution_memory SET evidence=? WHERE memory_id=?",("[\"tamper\"]",row[0]))
    elif mutation=="transition_candidate":
        row=conn.execute("SELECT transition_id FROM transitions LIMIT 1").fetchone(); other_state=State(elements={"v":99}); save_state(conn, other_state); other=Candidate(tr.from_state_id, other_state, "tampered", 99); save_candidate(conn, other); conn.execute("UPDATE transitions SET candidate_id=? WHERE transition_id=?",(other.candidate_id,row[0]))
    else:
        row=conn.execute("SELECT transition_id FROM transitions LIMIT 1").fetchone(); conn.execute("UPDATE transitions SET to_state_id=? WHERE transition_id=?",(tr.from_state_id,row[0]))
    conn.commit(); conn.close()
    with pytest.raises(Exception): recover_partner_learning(str(path), instance_id, authorization=recovery_auth(str(path), instance_id), now="2026-09-25T12:00:00Z")

def test_full_chain_exact_replay_after_reopen_is_idempotent(tmp_path):
    path=tmp_path/"replay.db"; tr,result,instance_id=build_chain(str(path)); recover_partner_learning(str(path), instance_id, authorization=recovery_auth(str(path), instance_id), now="2026-09-25T12:00:00Z")
    conn=connect(str(path)); admission=admit_partner_candidate(classification_id="class:1",result_id="result:1",candidate_digest="prov:1",evidence_refs=("ev:1",),classification_verified=True,replay_verified=True,receipt_received=True,core_verified=True)
    request=build_request(candidate_id=(conn.execute("SELECT candidate_id FROM transitions WHERE transition_id=?",(tr.transition_id,)).fetchone()[0]),result_id="result:1",contract_id="contract:1",provenance_digest="prov:1",evidence_refs=("ev:1",),state_digest=tr.to_state_id,admission_verified=True)
    again=commit_admitted_partner_learning(conn,admission=admission,request=request,instance_id=instance_id,transition_id=tr.transition_id,state_id=tr.to_state_id,outcome="accepted",actor="partner")
    assert again.memory_id==result.memory_id
    assert conn.execute("SELECT count(*) FROM evolution_memory").fetchone()[0]==1
    assert conn.execute("SELECT count(*) FROM audit_events WHERE event_id LIKE 'partner-learning:%'").fetchone()[0]==1
    conn.close()
