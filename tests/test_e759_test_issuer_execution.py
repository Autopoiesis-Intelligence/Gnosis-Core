import pytest

from gnosis.core import Candidate, State
from gnosis.evolution.provenance import build_provenance, canonical_digest
from gnosis.instances.instance import Instance
from gnosis.reflection.authorization_validity import AuthorizationValidity
from gnosis.reflection.authority import ExecutionCommitRequest, ExecutionIntentSnapshot
from gnosis.reflection.execution_adapter import SQLiteExecutionCommitAdapter
from gnosis.reflection.test_issuer import (
    TestAuthorizationIssuer,
    issue_for_provenance_for_test,
    to_execution_authorization_for_test,
)
from gnosis.storage import connect, load_instance, save_instance


def _provenance(candidate, parent_state):
    observations = {"result": "ok", "candidate_id": candidate.candidate_id}
    return build_provenance(
        candidate_id=candidate.candidate_id,
        parent_state_id=parent_state.state_id,
        parent_state_digest=parent_state.state_id,
        proposed_state_digest=candidate.proposed_state.state_id,
        observations=observations,
        proposed_state_content_id=candidate.proposed_state.content_id,
        candidate_binding_digest=candidate.binding_digest(parent_state.state_id),
        evidence_digest=canonical_digest(observations),
        evaluation_status="PASS",
        shadow_status="UNCHANGED",
        invariant_status="PRESERVED",
        governance_decision="ALLOW",
    )


def test_e759_test_issuer_reaches_actual_sqlite_mutation():
    conn = connect()
    instance = Instance.create_root("user-1", State(elements={"a": 1}))
    save_instance(conn, instance)

    parent_state = instance.engine.state
    candidate = Candidate(
        parent_state.state_id,
        parent_state.with_elements({"a": 2}),
        "e759-test-issuer",
    )
    record = instance.engine.step(candidate)
    provenance = _provenance(candidate, parent_state)

    issuer = TestAuthorizationIssuer(secret=b"e7.59-runtime-test")
    issued = issue_for_provenance_for_test(
        issuer,
        provenance,
        policy_version="policy:e7.59-test",
        expires_at=100,
    )
    assert issuer.verify(issued)

    execution_auth = to_execution_authorization_for_test(issuer, issued)
    request = ExecutionCommitRequest(
        execution_auth,
        ExecutionIntentSnapshot.from_provenance(provenance),
        provenance.provenance_id,
        provenance.evolution_identity,
        provenance,
        AuthorizationValidity(
            issued.authorization_id,
            "policy:e7.59-test",
            "e7.59-validity",
        ),
    )

    result = SQLiteExecutionCommitAdapter().commit(
        conn,
        instance,
        candidate,
        record,
        request,
        actor="e7.59-test",
    )

    persisted = load_instance(conn, instance.instance_id)
    assert result.resulting_state_id == candidate.proposed_state.state_id
    assert persisted.engine.state.state_id == candidate.proposed_state.state_id
    assert result.receipt.matches_request(request)
    assert conn.execute(
        "SELECT count(*) FROM audit_events WHERE event_id = ?",
        (f"execution-authorization:{issued.authorization_id}",),
    ).fetchone()[0] == 1
    conn.close()


def test_e759_raw_execution_authorization_is_not_a_test_issuer_artifact():
    issuer = TestAuthorizationIssuer(secret=b"e7.59-adversarial-test")
    issued = issuer.issue(
        request_provenance="p",
        evolution_identity="e",
        parent_state_digest="s",
        policy_version="policy:e7.59-test",
        scope=("test:execute",),
        expires_at=100,
    )
    forged = type(issued)(
        **{
            **issued.__dict__,
            "signature": "forged",
        }
    )
    assert issuer.verify(issued)
    assert not issuer.verify(forged)
