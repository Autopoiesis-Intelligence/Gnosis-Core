import pytest
from gnosis.core import Candidate, State
from gnosis.core.durable_commit import persist_authorized_transition
from gnosis.core.governance import AuthorizationPackage
from gnosis.core.rule_proposal import RuleProposal
from gnosis.instances.instance import Instance
from gnosis.storage import connect, recover_instance, save_instance, verify_durable_graph
from gnosis.storage.repositories import transition_id

def test_domain_lineage_transition_is_persistent_and_recoverable(tmp_path):
    path=tmp_path/"lineage.sqlite"
    conn=connect(path)
    instance=Instance.create_root("u",State(elements={"root":0}))
    save_instance(conn,instance)
    proposed=instance.engine.state.with_elements({"root":0,"evolved":1})
    candidate=Candidate(instance.engine.state.state_id,proposed,"lineage-test")
    transition=instance.engine.step(candidate)
    proposal=RuleProposal("rule:x","gap:x","finding:x",("e1",),"supported")
    auth=AuthorizationPackage("auth:x",proposal.proposal_id,("e1",),(),"shadow:x","AUTHORIZED")
    record=persist_authorized_transition(conn,auth,proposal,instance,candidate,transition,actor="core")
    tid=transition_id(transition)
    assert record.transition_id==tid
    row=conn.execute("SELECT transition_id FROM transitions WHERE transition_id=?",(tid,)).fetchone()
    audit=conn.execute("SELECT transition_id FROM audit_events WHERE transition_id=?",(tid,)).fetchone()
    assert tuple(row)==(tid,)
    assert tuple(audit)==(tid,)
    assert verify_durable_graph(conn)[0]==2
    conn.close()
    reopened=connect(path)
    recovered=recover_instance(reopened,instance.instance_id)
    assert recovered.engine.state.state_id==proposed.state_id
    assert verify_durable_graph(reopened)[0]==2

def test_corrupted_transition_audit_breaks_recovery(tmp_path):
    path=tmp_path/"corrupt.sqlite"
    conn=connect(path)
    instance=Instance.create_root("u",State(elements={"root":0}))
    save_instance(conn,instance)
    proposed=instance.engine.state.with_elements({"evolved":1})
    candidate=Candidate(instance.engine.state.state_id,proposed,"corrupt-test")
    transition=instance.engine.step(candidate)
    proposal=RuleProposal("rule:x","gap:x","finding:x",("e1",),"supported")
    auth=AuthorizationPackage("auth:x",proposal.proposal_id,("e1",),(),"shadow:x","AUTHORIZED")
    persist_authorized_transition(conn,auth,proposal,instance,candidate,transition,actor="core")
    tid=transition_id(transition)
    conn.execute("DELETE FROM audit_events WHERE transition_id=?",(tid,))
    with pytest.raises(Exception,match="audit evidence"):
        recover_instance(conn,instance.instance_id)
