"""E7.59-A real execution-boundary experiment."""
from __future__ import annotations

import pytest

from gnosis.core import Candidate, State
from gnosis.evolution.provenance import build_provenance, canonical_digest
from gnosis.instances.instance import Instance
from gnosis.reflection.authority import (
    ExecutionAuthorization,
    ExecutionCommitRequest,
    ExecutionIntentSnapshot,
)
from gnosis.reflection.authorization_validity import AuthorizationValidity
from gnosis.reflection.execution_adapter import SQLiteExecutionCommitAdapter
from gnosis.storage import connect, load_instance, save_instance


def test_forged_looking_authorization_reaches_real_boundary_without_trusted_issuer():
    conn = connect()
    instance = Instance.create_root("user-1", State(elements={"a": 1}))
    save_instance(conn, instance)
    initial_state_id = instance.engine.state.state_id

    proposed = instance.engine.state.with_elements({"b": 2})
    candidate = Candidate(initial_state_id, proposed, "e7-59-forged")
    record = instance.engine.step(candidate)

    observations = {"result": "ok"}
    provenance = build_provenance(
        candidate_id=candidate.candidate_id,
        parent_state_id=initial_state_id,
        parent_state_digest=initial_state_id,
        proposed_state_digest=proposed.state_id,
        observations=observations,
        proposed_state_content_id=proposed.content_id,
        candidate_binding_digest=candidate.binding_digest(initial_state_id),
        evidence_digest=canonical_digest(observations),
        evaluation_status="PASS",
        shadow_status="UNCHANGED",
        invariant_status="PRESERVED",
        governance_decision="ALLOW",
    )

    # Deliberately constructed without TrustedOwnerIssuer.
    validity = AuthorizationValidity(
        "forged-e2e-approval", "policy-1", "ev-1"
    )
    authorization = ExecutionAuthorization(
        provenance.provenance_id,
        True,
        provenance.evolution_identity,
        validity.authorization_id,
    )
    request = ExecutionCommitRequest(
        authorization,
        ExecutionIntentSnapshot.from_provenance(provenance),
        provenance.provenance_id,
        provenance.evolution_identity,
        provenance,
        validity,
    )

    before = load_instance(conn, instance.instance_id).engine.state.state_id

    try:
        with pytest.raises(PermissionError):
            SQLiteExecutionCommitAdapter().commit(
                conn, instance, candidate, record, request, actor="user-1"
            )

        after = load_instance(conn, instance.instance_id).engine.state.state_id
        transition_count = conn.execute(
            "SELECT count(*) FROM transitions WHERE candidate_id=?",
            (candidate.candidate_id,),
        ).fetchone()[0]
        receipt_count = conn.execute(
            "SELECT count(*) FROM audit_events WHERE transition_id IS NOT NULL AND transition_id=?",
            (record.transition_id,),
        ).fetchone()[0]

        assert after == before
        assert transition_count == 0
        assert receipt_count == 0
    finally:
        conn.close()
