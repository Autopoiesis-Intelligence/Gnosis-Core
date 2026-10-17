"""R2 adversarial proof: Federation evidence may reach Core commit only through every trust gate."""
import pytest
from gnosis.core import Candidate, State, TestResult, TransitionRecord
from gnosis.evolution.federation_admission import admit_federation_evidence, build_core_provenance
from gnosis.instances.instance import Instance
from gnosis.reflection.authority import ExecutionAuthorization, ExecutionCommitRequest, ExecutionIntentSnapshot
from gnosis.reflection.authorization_validity import AuthorizationValidity
from gnosis.reflection.execution_adapter import SQLiteExecutionCommitAdapter
from gnosis.storage import load_instance, save_instance
from registry.core_handoff import create_handoff


def build_request(candidate, parent_state, proposed_state):
    handoff = create_handoff(
        {"result": "AUTHORIZED", "authorization_sha256": "a" * 64},
        {"candidate_id": candidate.candidate_id, "source_id": "s1", "resource_id": "r1"},
        "core-evolution",
        "propose",
        ["e1"],
    )["handoff"]
    envelope = admit_federation_evidence(handoff, {"observation": "value"})
    provenance = build_core_provenance(
        envelope,
        parent_state_id=parent_state.state_id,
        parent_state_digest=parent_state.state_id,
        proposed_state_digest=proposed_state.state_id,
        proposed_state_content_id=proposed_state.content_id,
        candidate_binding_digest=candidate.binding_digest(parent_state.state_id),
        evaluation_status="PASS",
        shadow_status="PASS",
        invariant_status="PASS",
        governance_decision="ALLOW",
    )
    validity = AuthorizationValidity("auth-e2e", "policy-1", "ev-1")
    authorization = ExecutionAuthorization(
        request_provenance=provenance.provenance_id,
        owner_approved=True,
        evolution_identity=provenance.evolution_identity,
        approval_id=validity.authorization_id,
    )
    request = ExecutionCommitRequest(
        authorization,
        ExecutionIntentSnapshot.from_provenance(provenance),
        provenance.provenance_id,
        provenance.evolution_identity,
        provenance,
        validity,
    )
    return request


def test_federation_e2e_reaches_trusted_commit_boundary_atomically(sqlite_conn):
    instance = Instance.create_root("trusted-owner", State(elements={"a": 1}))
    save_instance(sqlite_conn, instance)
    parent_state = instance.engine.state
    proposed_state = parent_state.with_elements({"b": 2})
    candidate = Candidate(parent_state.state_id, proposed_state, "federation-e2e")
    request = build_request(candidate, parent_state, proposed_state)

    # The request and candidate are bound, but the transition record lies about
    # the authorized result. Exercise the real transaction-owning commit adapter.
    incomplete_record = TransitionRecord(
        from_state_id=parent_state.state_id,
        to_state_id="incomplete-state",
        candidate_id=candidate.candidate_id,
        test_result=TestResult(passed=True, reasons=("deliberately incomplete",)),
        accepted=True,
        reason="incomplete",
    )

    with pytest.raises(PermissionError, match="transition record result does not match authorized evolution"):
        SQLiteExecutionCommitAdapter().commit(
            sqlite_conn,
            instance,
            candidate,
            incomplete_record,
            request,
            actor="trusted-owner",
        )

    # Authorization consumption and all other writes must roll back together.
    assert sqlite_conn.execute(
        "SELECT event_hash FROM audit_events WHERE event_id=?",
        ("execution-authorization:auth-e2e",),
    ).fetchone() is None
    assert sqlite_conn.execute("SELECT count(*) FROM transitions").fetchone()[0] == 0
    assert sqlite_conn.execute("SELECT count(*) FROM candidates").fetchone()[0] == 0
    assert load_instance(sqlite_conn, instance.instance_id).engine.state.state_id == parent_state.state_id


def test_tampered_federation_candidate_is_rejected():
    handoff = create_handoff(
        {"result": "AUTHORIZED", "authorization_sha256": "a" * 64},
        {"candidate_id": "c1", "source_id": "s1", "resource_id": "r1"},
        "core-evolution",
        "propose",
        ["e1"],
    )["handoff"]
    handoff["candidate_id"] = "forged"
    with pytest.raises(PermissionError):
        admit_federation_evidence(handoff, {"observation": "value"})
