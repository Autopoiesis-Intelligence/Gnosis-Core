from __future__ import annotations

import pytest

from gnosis.self_learning.collaboration_authorization import (
    PreconditionEvidence,
    issue_execution_authorization,
)
from gnosis.self_learning.collaboration_controlled_target import (
    ControlledTarget,
    ControlledTargetAdapter,
)
from gnosis.self_learning.collaboration_runtime import build_trusted_collaboration_runtime


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


def _runtime(adapter):
    evidence = PreconditionEvidence(
        source_id="trusted-review-engine",
        target_revision="target-r1",
        evidence_revision="evidence-r1",
        observed_conditions=("review-current",),
        provenance="trusted-chain:r1",
    )
    return build_trusted_collaboration_runtime(
        target_revision_resolver=lambda resource: "target-r1",
        evidence_resolver=lambda digest: evidence,
        external_action=adapter.execute,
    )


def test_authorized_execution_produces_real_before_after_transition():
    target = ControlledTarget("repo:public/project", {"title": "before"})
    adapter = ControlledTargetAdapter(target)
    before = target.snapshot()

    observation = _runtime(adapter).execute(
        authorization=_authorization(),
        review_id="review-1", review_digest="sha256:review",
        proposal_id="proposal-1", proposal_revision="r1",
        action_class="CREATE_PUBLIC_ISSUE_OR_PR",
        target_resource="repo:public/project", requested_scope="issue:create",
        executor_id="executor-1", privacy_classification="PUBLIC_APPROVED",
        now="2026-01-01T00:00:00Z", action_payload={"title": "after"},
    )

    assert observation.effect_applied is True
    assert observation.target_before == before
    assert observation.target_before.content_digest != observation.target_after.content_digest
    assert observation.target_before.revision == "r0"
    assert observation.target_after.revision == "r1"


def test_unauthorized_execution_does_not_reach_effect_boundary():
    target = ControlledTarget("repo:public/project", {"title": "before"})
    adapter = ControlledTargetAdapter(target)
    before = target.snapshot()
    runtime = build_trusted_collaboration_runtime(
        target_revision_resolver=lambda resource: "target-r2",
        evidence_resolver=lambda digest: None,
        external_action=adapter.execute,
    )

    with pytest.raises(PermissionError):
        runtime.execute(
            authorization=_authorization(),
            review_id="review-1", review_digest="sha256:review",
            proposal_id="proposal-1", proposal_revision="r1",
            action_class="CREATE_PUBLIC_ISSUE_OR_PR",
            target_resource="repo:public/project", requested_scope="issue:create",
            executor_id="executor-1", privacy_classification="PUBLIC_APPROVED",
            now="2026-01-01T00:00:00Z", action_payload={"title": "must-not-run"},
        )

    assert target.snapshot() == before


def test_identical_state_update_is_observed_as_no_effect():
    target = ControlledTarget("repo:public/project", {"title": "same"})
    observation = ControlledTargetAdapter(target).execute(
        type("Request", (), {"parameters": {"title": "same"}})()
    )

    assert observation.effect_applied is False
    assert observation.target_before == observation.target_after
