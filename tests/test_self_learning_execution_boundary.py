import pytest
from gnosis.self_learning.bridge import approve_core_mutation, create_core_mutation_proposal
from gnosis.self_learning.cycle import build_verified_cycle
from gnosis.self_learning.execution import execute_approved_core_proposal
from gnosis.reflection.authority import (
    ExecutionAuthorization, ExecutionCommitRequest, ExecutionIntentSnapshot,
)

def valid_proposal():
    cycle = build_verified_cycle(
        "subject-test", knowledge={"rule": "bounded"}, reason="generalizable"
    )
    record = cycle
    from gnosis.self_learning.integration import create_integration_record
    from gnosis.self_learning.promotion import propose_promotion, decide_promotion
    from gnosis.self_learning.lineage import record_version
    # Reconstruct the same deterministic integration path through the canonical cycle.
    # The cycle result exposes only identities, so use its IDs to build the proposal
    # fixture directly from the canonical stage implementations.
    from gnosis.self_learning.knowledge import propose_knowledge_update, apply_knowledge_update
    from gnosis.self_learning.lifecycle import verify_lifecycle
    from gnosis.self_learning.ledger import create_event
    events=[]; previous="GENESIS"
    for i, event_type in enumerate(("DATABASE","FINDING","PROPOSAL","VALIDATION","GOVERNANCE","EXECUTION_PLAN","RECEIPT")):
        event=create_event(event_type,"subject-test",{"stage":i},previous)
        events.append(event); previous=event.event_digest
    lifecycle=verify_lifecycle(events,"subject-test")
    update=apply_knowledge_update(propose_knowledge_update(
        subject_id="subject-test",
        evidence_digest=events[-1].event_digest,
        knowledge={"rule":"bounded"},
        lifecycle=lifecycle,
        scope="common-self-learning",
        shareable=True,
    ))
    version=record_version(update)
    promotion=decide_promotion(
        propose_promotion(version,evidence_refs=(events[-1].event_digest,),reason="generalizable"),
        decision="ACCEPTED", reviewer="test",
    )
    integration=create_integration_record(
        promotion, action="controlled-core-learning-integration"
    )
    return approve_core_mutation(
        create_core_mutation_proposal(integration), approver="test"
    )

def test_execution_adapter_fails_closed_without_owner_authorization():
    proposal=valid_proposal()
    auth=ExecutionAuthorization(
        request_provenance="p",
        owner_approved=False,
        evolution_identity="e",
        approval_id="",
    )
    snapshot=ExecutionIntentSnapshot(
        provenance_id="p", execution_id="x",
        parent_state_id="parent", parent_state_digest="sha256:p",
        evolution_identity="e", candidate_binding_digest="sha256:c",
        proposed_state_content_id="sha256:content",
    )
    request=ExecutionCommitRequest(auth,snapshot,"p","e",object())
    with pytest.raises(PermissionError):
        execute_approved_core_proposal(
            proposal,request,conn=object(),instance=object(),
            candidate=object(),record=object(),actor="test"
        )
