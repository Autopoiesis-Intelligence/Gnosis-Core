"""Governed E7.76 -> external-provider -> E7.77 execution boundary."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from .collaboration_authorization import (
    ExecutionAuthorization,
    TrustedEvidenceResolver,
    TargetRevisionResolver,
)
from .collaboration_execution_evidence import ExecutionEvidence, create_execution_evidence
from .collaboration_provider import ExternalActionProvider, normalize_provider_result
from .collaboration_runtime import build_trusted_collaboration_runtime


@dataclass(frozen=True)
class GovernedExternalResult:
    evidence: ExecutionEvidence
    provider_result: Mapping[str, object] | None


def execute_governed_external_action(
    *,
    authorization: ExecutionAuthorization,
    review_id: str,
    review_digest: str,
    proposal_id: str,
    proposal_revision: str,
    action_class: str,
    target_resource: str,
    requested_scope: str,
    executor_id: str,
    privacy_classification: str,
    now: str,
    target_before: str,
    target_revision_resolver: TargetRevisionResolver,
    evidence_resolver: TrustedEvidenceResolver,
    provider: ExternalActionProvider,
    authorization_id: str,
    attempt_id: str,
    ordering_evidence: str,
    provenance_refs: tuple[str, ...],
    current_revocation_revision: str | None = None,
    action_payload: Mapping[str, object],
) -> GovernedExternalResult:
    """Run the provider only after E7.76 allows the request and emit E7.77 evidence."""
    called = False
    provider_result: Mapping[str, object] | None = None
    result_status = "REJECTED_BY_BOUNDARY"
    target_after = target_before
    reconciliation_status = "REJECTED"

    def guarded(payload: Mapping[str, object]) -> Mapping[str, object]:
        nonlocal called, provider_result, result_status, target_after, reconciliation_status
        called = True
        raw = provider(payload)
        normalized = normalize_provider_result(raw)
        provider_result = normalized.result_metadata
        target_after = normalized.target_after
        result_status = "SUCCEEDED"
        reconciliation_status = "RECONCILED"
        return provider_result

    runtime = build_trusted_collaboration_runtime(
        target_revision_resolver=target_revision_resolver,
        evidence_resolver=evidence_resolver,
        external_action=guarded,
    )
    try:
        runtime.execute(
            authorization=authorization,
            review_id=review_id,
            review_digest=review_digest,
            proposal_id=proposal_id,
            proposal_revision=proposal_revision,
            action_class=action_class,
            target_resource=target_resource,
            requested_scope=requested_scope,
            executor_id=executor_id,
            privacy_classification=privacy_classification,
            now=now,
            current_revocation_revision=current_revocation_revision,
            action_payload=action_payload,
        )
    except PermissionError:
        pass
    except Exception:
        result_status = "FAILED"
        reconciliation_status = "UNKNOWN"

    evidence = create_execution_evidence(
        authorization_id=authorization_id,
        review_id=review_id,
        proposal_revision=proposal_revision,
        action=action_class,
        target_resource=target_resource,
        authorized_scope=requested_scope,
        executor_id=executor_id,
        attempt_id=attempt_id,
        ordering_evidence=ordering_evidence,
        result_status=result_status,
        target_before=target_before,
        target_after=target_after,
        privacy_classification=privacy_classification,
        reconciliation_status=reconciliation_status,
        provenance_refs=provenance_refs,
    )
    if not called and result_status == "SUCCEEDED":
        raise AssertionError("successful evidence without provider execution")
    return GovernedExternalResult(evidence=evidence, provider_result=provider_result)
