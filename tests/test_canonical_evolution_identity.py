from dataclasses import replace

import pytest

from gnosis.reflection.authority import (
    ExecutionAuthorization,
    ExecutionCommitRequest,
    ExecutionIntentSnapshot,
    require_execution_commit,
)


def _request(provenance):
    identity = provenance.evolution_identity
    authorization = ExecutionAuthorization(
        request_provenance=provenance.provenance_id,
        owner_approved=True,
        evolution_identity=identity,
        approval_id="unit-test-approval",
    )
    return ExecutionCommitRequest(
        authorization=authorization,
        intent_snapshot=ExecutionIntentSnapshot.from_provenance(provenance),
        request_provenance=provenance.provenance_id,
        evolution_identity=identity,
        provenance=provenance,
    )


def test_canonical_identity_matches_gate_for_existing_provenance(provenance):
    request = _request(provenance)

    require_execution_commit(request)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("evaluator_identity_ref", "evaluator://test"),
        ("evaluator_identity_version", "v2"),
    ],
)
def test_stale_request_rejected_when_evaluator_identity_changes(provenance, field, value):
    request = _request(provenance)
    changed_provenance = replace(provenance, **{field: value})
    stale_request = replace(request, provenance=changed_provenance)

    with pytest.raises(PermissionError, match="canonical"):
        require_execution_commit(stale_request)


def test_populated_evaluator_identity_has_consistent_distinct_identity(provenance):
    populated = replace(
        provenance,
        evaluator_identity_ref="evaluator://test",
        evaluator_identity_version="v2",
    )

    assert populated.evolution_identity != provenance.evolution_identity
    require_execution_commit(_request(populated))


def test_lifecycle_status_does_not_change_evolution_identity(provenance):
    status_changed = replace(provenance, status="SUPERSEDED")

    assert status_changed.evolution_identity == provenance.evolution_identity
    require_execution_commit(_request(status_changed))
