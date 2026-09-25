from __future__ import annotations

import pytest

from gnosis.self_learning.collaboration_authorization import PreconditionEvidence
from gnosis.self_learning.governed_external_adapter import execute_governed_external_action
from gnosis.self_learning.fake_external_provider import FakeExternalProvider
from tests.test_collaboration_runtime import _authorization


def _evidence():
    return PreconditionEvidence(
        source_id="trusted-review-engine",
        target_revision="target-r1",
        evidence_revision="evidence-r1",
        observed_conditions=("review-current",),
        provenance="trusted-chain:r1",
    )


def _kwargs():
    return dict(
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
        target_before="target-r1",
        target_revision_resolver=lambda resource: "target-r1",
        evidence_resolver=lambda digest: _evidence(),
        authorization_id="auth-1",
        attempt_id="attempt-1",
        ordering_evidence="order-1",
        provenance_refs=("prov-1",),
    )


def test_denial_never_calls_provider():
    calls = []
    result = execute_governed_external_action(
        **_kwargs(),
        provider=lambda payload: calls.append(payload) or {"target_after": "target-r2"},
        action_payload={"title": "test"},
    )
    assert calls == []
    assert result.evidence.result_status == "REJECTED_BY_BOUNDARY"


def test_allow_calls_provider_and_produces_success_evidence():
    provider = FakeExternalProvider(target_after="target-r2")
    result = execute_governed_external_action(**_kwargs(), provider=provider)
    assert provider.calls == [{"title": "test"}]
    assert result.evidence.result_status == "SUCCEEDED"
    assert result.evidence.target_after == "target-r2"
    assert result.evidence.reconciliation_status == "RECONCILED"


def test_provider_failure_is_not_success():
    provider = FakeExternalProvider(fail=True)
    result = execute_governed_external_action(**_kwargs(), provider=provider)
    assert result.evidence.result_status == "FAILED"
    assert result.evidence.reconciliation_status == "UNKNOWN"
