from __future__ import annotations

import pytest

from gnosis.self_learning.collaboration_authorization import (
    PreconditionEvidence,
    issue_execution_authorization,
)
from gnosis.self_learning.collaboration_runtime import (
    ExternalActionRequest,
    ExternalExecutionReceipt,
    build_trusted_collaboration_runtime,
)


def _authorization():
    evidence = PreconditionEvidence(
        source_id="trusted-review-engine",
        target_revision="target-r1",
        evidence_revision="evidence-r1",
        observed_conditions=("review-current",),
        provenance="trusted-chain:r1",
    )
    return issue_execution_authorization(
        review_id="review-1",
        review_digest="sha256:review",
        review_decision="ACCEPTED",
        review_proposal_id="proposal-1",
        review_proposal_revision="r1",
        proposal_id="proposal-1",
        proposal_revision="r1",
        action_class="CREATE_PUBLIC_ISSUE_OR_PR",
        target_resource="repo:public/project",
        authorized_scope="issue:create",
        executor_id="executor-1",
        authorization_basis="review-1",
        privacy_classification="PUBLIC_APPROVED",
        issuance_revision="auth-r1",
        expires_at="2099-01-01T00:00:00Z",
        preconditions=("review-current",),
        authorized_target_revision="target-r1",
        precondition_evidence=evidence,
    )


def test_runtime_denies_before_external_side_effect():
    calls = []
    runtime = build_trusted_collaboration_runtime(
        target_revision_resolver=lambda resource: "target-r2",
        evidence_resolver=lambda digest: None,
        external_action=lambda payload: calls.append(payload) or ExternalExecutionReceipt(\n            authorization_id=auth.authorization_id if "auth" in locals() else "unused",\n            effect_id="effect-denied", effect_status="not-run", evidence_digest="sha256:none"\n        ),
    )
    with pytest.raises(PermissionError):
        runtime.execute(
            authorization=_authorization(),
            review_id="review-1",
            review_digest="sha256:review",
            proposal_id="proposal-1",
            proposal_revision="r1",
            action_class="CREATE_PUBLIC_ISSUE_OR_PR",
            target_resource="repo:public/project",
            requested_scope="issue:create",
            executor_id="executor-1",
            privacy_classification="PUBLIC_APPROVED",
            now="2026-01-01T00:00:00Z",
            action_payload={"title": "must-not-run"},
        )
    assert calls == []


def test_runtime_executes_only_after_authorization():
    auth = _authorization()
    evidence = PreconditionEvidence(
        source_id="trusted-review-engine",
        target_revision="target-r1",
        evidence_revision="evidence-r1",
        observed_conditions=("review-current",),
        provenance="trusted-chain:r1",
    )
    calls = []
    runtime = build_trusted_collaboration_runtime(
        target_revision_resolver=lambda resource: "target-r1",
        evidence_resolver=lambda digest: evidence,
        external_action=lambda payload: calls.append(payload) or ExternalExecutionReceipt(\n            authorization_id=auth.authorization_id, effect_id="effect-1", effect_status="executed", evidence_digest="sha256:evidence-1"\n        ),
    )
    result = runtime.execute(
        authorization=auth,
        review_id="review-1",
        review_digest="sha256:review",
        proposal_id="proposal-1",
        proposal_revision="r1",
        action_class="CREATE_PUBLIC_ISSUE_OR_PR",
        target_resource="repo:public/project",
        requested_scope="issue:create",
        executor_id="executor-1",
        privacy_classification="PUBLIC_APPROVED",
        now="2026-01-01T00:00:00Z",
        action_payload={"title": "allowed"},
    )
    assert result.effect_id == "effect-1"
    assert len(calls) == 1
    request = calls[0]
    assert isinstance(request, ExternalActionRequest)
    assert request.authorization_id == auth.authorization_id
    assert request.action_class == auth.action_class
    assert request.target_resource == auth.target_resource
    assert request.authorized_scope == auth.authorized_scope
    assert request.executor_id == auth.executor_id
    assert request.privacy_classification == auth.privacy_classification
    assert request.parameters == {"title": "allowed"}


def test_runtime_requires_callable_trusted_dependencies():
    with pytest.raises(TypeError):
        build_trusted_collaboration_runtime(
            target_revision_resolver=None,
            evidence_resolver=lambda digest: None,
            external_action=lambda payload: None,
        )


def test_runtime_builds_canonical_request_from_validated_authorization():
    auth = _authorization()
    evidence = PreconditionEvidence(
        source_id="trusted-review-engine",
        target_revision="target-r1",
        evidence_revision="evidence-r1",
        observed_conditions=("review-current",),
        provenance="trusted-chain:r1",
    )
    calls = []
    runtime = build_trusted_collaboration_runtime(
        target_revision_resolver=lambda resource: "target-r1",
        evidence_resolver=lambda digest: evidence,
        external_action=lambda request: calls.append(request) or ExternalExecutionReceipt(\n            authorization_id=auth.authorization_id, effect_id="effect-2", effect_status="executed", evidence_digest="sha256:evidence-2"\n        ),
    )
    runtime.execute(
        authorization=auth,
        review_id="review-1",
        review_digest="sha256:review",
        proposal_id="proposal-1",
        proposal_revision="r1",
        action_class="CREATE_PUBLIC_ISSUE_OR_PR",
        target_resource="repo:public/project",
        requested_scope="issue:create",
        executor_id="executor-1",
        privacy_classification="PUBLIC_APPROVED",
        now="2026-01-01T00:00:00Z",
        action_payload={"title": "allowed"},
    )
    assert isinstance(calls[0], ExternalActionRequest)
    assert calls[0].authorization_id == auth.authorization_id
    assert calls[0].target_resource == auth.target_resource
    assert calls[0].action_class == auth.action_class
    assert calls[0].authorized_scope == auth.authorized_scope
