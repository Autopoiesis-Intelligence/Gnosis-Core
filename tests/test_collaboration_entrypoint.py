from __future__ import annotations

import pytest

from gnosis.self_learning.collaboration_authorization import PreconditionEvidence, issue_execution_authorization
from gnosis.self_learning.collaboration_entrypoint import compose_collaboration_runtime
from gnosis.self_learning.collaboration_runtime import ExternalActionRequest


def _authorization():
    evidence = PreconditionEvidence(
        source_id="trusted-review-engine",
        target_revision="target-r1",
        evidence_revision="evidence-r1",
        observed_conditions=("review-current",),
        provenance="trusted-chain:r1",
    )
    return issue_execution_authorization(
        review_id="review-1", review_digest="sha256:review",
        review_decision="ACCEPTED", review_proposal_id="proposal-1",
        review_proposal_revision="r1", proposal_id="proposal-1", proposal_revision="r1",
        action_class="CREATE_PUBLIC_ISSUE_OR_PR", target_resource="repo:public/project",
        authorized_scope="issue:create", executor_id="executor-1",
        authorization_basis="review-1", privacy_classification="PUBLIC_APPROVED",
        issuance_revision="auth-r1", expires_at="2099-01-01T00:00:00Z",
        preconditions=("review-current",), authorized_target_revision="target-r1",
        precondition_evidence=evidence,
    )


def test_composition_owns_provider_wiring_and_executes_after_validation():
    evidence = PreconditionEvidence(
        source_id="trusted-review-engine",
        target_revision="target-r1",
        evidence_revision="evidence-r1",
        observed_conditions=("review-current",),
        provenance="trusted-chain:r1",
    )
    calls = []
    composition = compose_collaboration_runtime(
        target_revision_resolver=lambda resource: "target-r1",
        evidence_resolver=lambda digest: evidence,
        external_action=lambda payload: calls.append(payload) or "ok",
    )
    result = composition.execute(
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
        action_payload={"title": "allowed"},
    )
    assert result == "ok"
    assert len(calls) == 1
    assert isinstance(calls[0], ExternalActionRequest)
    assert calls[0].parameters == {"title": "allowed"}


def test_request_cannot_replace_provider_wiring():
    evidence = PreconditionEvidence(
        source_id="trusted-review-engine",
        target_revision="target-r1",
        evidence_revision="evidence-r1",
        observed_conditions=("review-current",),
        provenance="trusted-chain:r1",
    )
    calls = []
    composition = compose_collaboration_runtime(
        target_revision_resolver=lambda resource: "target-r1",
        evidence_resolver=lambda digest: evidence,
        external_action=lambda payload: calls.append(payload),
    )
    with pytest.raises(TypeError):
        composition.execute(
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
            extra_provider=lambda resource: "wrong",
        )
    assert calls == []
