"""R3.3 runtime integration tests: rejected learning cannot reach persistence."""
import pytest
from gnosis.core import Candidate, State, TestResult, TransitionRecord
from gnosis.storage.database import connect
from gnosis.storage.repositories import save_state, save_candidate
from gnosis.self_learning.partner_learning_adapter import build_request
from gnosis.self_learning.partner_learning_gate import admit_partner_candidate
from gnosis.self_learning.partner_learning_runtime import commit_admitted_partner_learning

def fixture():
    conn=connect(":memory:")
    parent=State(elements={"v":1}); proposed=parent.with_elements({"v":2})
    save_state(conn,parent); save_candidate(conn,Candidate(parent.state_id,proposed,"partner:test",1))
    candidate=conn.execute("SELECT candidate_id FROM candidates LIMIT 1").fetchone()[0]
    tr=TransitionRecord(parent.state_id,proposed.state_id,candidate,TestResult(True,("ok",)),True,"committed","test:partner")
    conn.execute("CREATE TABLE IF NOT EXISTS instances(instance_id TEXT PRIMARY KEY,parent_instance_id TEXT,owner_id TEXT,root_state_id TEXT,current_state_id TEXT,generation INTEGER,status TEXT,budget_total INTEGER,budget_spent INTEGER,created_at TEXT)")
    conn.execute("INSERT INTO instances VALUES(?,?,?,?,?,?,?,?,?,?)",("i",None,"o",parent.state_id,proposed.state_id,0,"active",10,1,"t"))
    conn.execute("CREATE TABLE IF NOT EXISTS transitions(transition_id TEXT PRIMARY KEY,instance_id TEXT,candidate_id TEXT,from_state_id TEXT,to_state_id TEXT,accepted INTEGER,reasons TEXT,test_rule_id TEXT,created_at TEXT)")
    conn.execute("INSERT INTO transitions VALUES(?,?,?,?,?,?,?,?,?)",(tr.transition_id,"i",candidate,parent.state_id,proposed.state_id,1,'["ok"]',"test:partner","t"))
    admission=admit_partner_candidate(classification_id="c",result_id="r",candidate_digest="p",evidence_refs=("ev",),classification_verified=True,replay_verified=True,receipt_received=True,core_verified=True)
    request=build_request(candidate_id=candidate,result_id="r",contract_id="ct",provenance_digest="p",evidence_refs=("ev",),state_digest=proposed.state_id,admission_verified=True)
    return conn,tr,admission,request

@pytest.mark.parametrize("mode",["noop","replay","unverified"])
def test_rejected_learning_never_reaches_persistence(mode):
    conn,tr,admission,request=fixture()
    before=conn.execute("SELECT count(*) FROM evolution_memory").fetchone()[0]

    if mode == "unverified":
        with pytest.raises(ValueError, match="all trust gates"):
            admit_partner_candidate(
                classification_id="c", result_id="r", candidate_digest="p",
                evidence_refs=("ev",), classification_verified=False,
                replay_verified=True, receipt_received=True, core_verified=True,
            )
    elif mode == "replay":
        with pytest.raises(ValueError, match="all trust gates"):
            admit_partner_candidate(
                classification_id="c", result_id="r", candidate_digest="p",
                evidence_refs=("ev",), classification_verified=True,
                replay_verified=False, receipt_received=True, core_verified=True,
            )
    else:
        with pytest.raises(ValueError, match="no-op"):
            commit_admitted_partner_learning(
                conn, admission=admission, request=request, instance_id="i",
                transition_id=tr.transition_id, state_id=tr.to_state_id,
                outcome="accepted", actor="partner",
                parent_state_digest=tr.to_state_id,
            )

    after=conn.execute("SELECT count(*) FROM evolution_memory").fetchone()[0]
    assert after == before
