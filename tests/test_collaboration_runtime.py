from __future__ import annotations

import pytest

from gnosis.self_learning.collaboration_authorization import (
    PreconditionEvidence,
    issue_execution_authorization,
)
from gnosis.self_learning.collaboration_runtime import (
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
        external_action=lambda payload: calls.append(payload),
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
        external_action=lambda payload: calls.append(payload) or "executed",
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
    assert result == "executed"
    assert calls == [{"title": "allowed"}]


def test_runtime_requires_callable_trusted_dependencies():
    with pytest.raises(TypeError):
        build_trusted_collaboration_runtime(
            target_revision_resolver=None,
            evidence_resolver=lambda digest: None,
            external_action=lambda payload: None,
        )
\n\ndef test_runtime_builds_canonical_request_from_validated_authorization():\n    auth = _authorization()\n    evidence = PreconditionEvidence(\n        source_id="trusted-review-engine",\n        target_revision="target-r1",\n        evidence_revision="evidence-r1",\n        observed_conditions=("review-current",),\n        provenance="trusted-chain:r1",\n    )\n    calls = []\n    runtime = build_trusted_collaboration_runtime(\n        target_revision_resolver=lambda resource: "target-r1",\n        evidence_resolver=lambda digest: evidence,\n        external_action=lambda request: calls.append(request) or "executed",\n    )\n    runtime.execute(\n        authorization=auth,\n        review_id="review-1",\n        review_digest="sha256:review",\n        proposal_id="proposal-1",\n        proposal_revision="r1",\n        action_class="CREATE_PUBLIC_ISSUE_OR_PR",\n        target_resource="repo:public/project",\n        requested_scope="issue:create",\n        executor_id="executor-1",\n        privacy_classification="PUBLIC_APPROVED",\n        now="2026-01-01T00:00:00Z",\n        action_payload={"title": "allowed"},\n    )\n    assert isinstance(calls[0], ExternalActionRequest)\n    assert calls[0].authorization_id == auth.authorization_id\n    assert calls[0].target_resource == auth.target_resource\n    assert calls[0].action_class == auth.action_class\n    assert calls[0].authorized_scope == auth.authorized_scope\n