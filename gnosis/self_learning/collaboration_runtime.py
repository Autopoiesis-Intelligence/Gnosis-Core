"""Trusted runtime boundary for E7.76 external collaboration actions.

The composition root owns this context. Callers submit requests only; they do not
supply target/evidence providers. Provider wiring is therefore an integration
boundary responsibility, not an authorization input.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping

from .collaboration_authorization import (
    ExecutionAuthorization,
    PreconditionEvidence,
    TrustedEvidenceResolver,
    TargetRevisionResolver,
    validate_execution_request,
)

ExternalAction = Callable[[Mapping[str, object]], object]


@dataclass(frozen=True)
class TrustedCollaborationRuntime:
    target_revision_resolver: TargetRevisionResolver
    evidence_resolver: TrustedEvidenceResolver
    external_action: ExternalAction

    def execute(
        self,
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
        current_revocation_revision: str | None = None,
        action_payload: Mapping[str, object],
    ) -> object:
        allowed = validate_execution_request(
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
            target_revision_resolver=self.target_revision_resolver,
            evidence_resolver=self.evidence_resolver,
            now=now,
            current_revocation_revision=current_revocation_revision,
        )
        if not allowed:
            raise PermissionError("E7.76 authorization denied")
        return self.external_action(action_payload)


def build_trusted_collaboration_runtime(
    *,
    target_revision_resolver: TargetRevisionResolver,
    evidence_resolver: TrustedEvidenceResolver,
    external_action: ExternalAction,
) -> TrustedCollaborationRuntime:
    """Composition-root factory.

    Production code should construct this once from trusted providers and keep
    the resulting runtime behind the external-action execution boundary.
    """
    if not callable(target_revision_resolver):
        raise TypeError("trusted target resolver is required")
    if not callable(evidence_resolver):
        raise TypeError("trusted evidence resolver is required")
    if not callable(external_action):
        raise TypeError("external action executor is required")
    return TrustedCollaborationRuntime(
        target_revision_resolver=target_revision_resolver,
        evidence_resolver=evidence_resolver,
        external_action=external_action,
    )
