import pytest
from gnosis.self_learning.lineage import KnowledgeVersion
from gnosis.self_learning.promotion import propose_promotion, decide_promotion
from gnosis.self_learning.integration import create_integration_record
from gnosis.self_learning.bridge import create_core_mutation_proposal, approve_core_mutation

def accepted_record():
    v=KnowledgeVersion("sha256:v","u","flow","common","sha256:k","GENESIS")
    p=decide_promotion(propose_promotion(v,evidence_refs=("sha256:e",),reason="generalizable"),decision="ACCEPTED",reviewer="r")
    return create_integration_record(p,action="merge-approved-knowledge")

def test_bridge_is_explicit():
    proposal=create_core_mutation_proposal(accepted_record())
    assert proposal.status=="PROPOSED"
    approved=approve_core_mutation(proposal,approver="core-governance")
    assert approved.status=="APPROVED"

def test_bridge_rejects_non_common_target():
    r=accepted_record()
    r=type(r)(r.integration_id,r.proposal_id,r.version_id,"partner-private",r.action,r.status,r.authority)
    with pytest.raises(ValueError): create_core_mutation_proposal(r)

def test_bridge_does_not_execute():
    proposal=create_core_mutation_proposal(accepted_record())
    assert proposal.authority=="core-bridge-proposal-only"
