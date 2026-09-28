"""Trusted runtime boundary for E7.76 external collaboration actions.

The composition root owns this context. Callers submit requests only; they do not
supply target/evidence providers. Provider wiring is therefore an integration
boundary responsibility, not an authorization input.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping, Protocol

from .collaboration_authorization import (
    ExecutionAuthorization,
    TrustedEvidenceResolver,
    TargetRevisionResolver,
    validate_execution_request,
)

@dataclass(frozen=True)
class ExternalActionRequest:
    """Canonical, validated execution envelope passed to an external adapter."""

    authorization_id: str
    action_class: str
    target_resource: str
    authorized_scope: str
    executor_id: str
    privacy_classification: str
    parameters: Mapping[str, object]


@dataclass(frozen=True)
class ExternalExecutionReceipt:
    """Explicit receipt returned by an external-action boundary."""

    authorization_id: str
    effect_id: str
    effect_status: str
    evidence_digest: str

    def __post_init__(self) -> None:
        if not all(value.strip() for value in (
            self.authorization_id, self.effect_id, self.effect_status, self.evidence_digest
        )):
            raise ValueError("external execution receipt fields are required")


class ExternalActionPort(Protocol):
    """Bounded port: receives only the canonical request and returns a receipt."""

    def __call__(self, request: ExternalActionRequest) -> ExternalExecutionReceipt: ...


ExternalAction = Callable[[ExternalActionRequest], ExternalExecutionReceipt]


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
        request = ExternalActionRequest(
            authorization_id=authorization.authorization_id,
            action_class=action_class,
            target_resource=target_resource,
            authorized_scope=requested_scope,
            executor_id=executor_id,
            privacy_classification=privacy_classification,
            parameters=dict(action_payload),
        )
        receipt = self.external_action(request)
        if not isinstance(receipt, ExternalExecutionReceipt):
            raise TypeError("external action adapter must return an execution receipt")
        if receipt.authorization_id != authorization.authorization_id:
            raise ValueError("execution receipt is not bound to authorization")
        return receipt


def build_trusted_collaboration_runtime(
    *,
    target_revision_resolver: TargetRevisionResolver,
    evidence_resolver: TrustedEvidenceResolver,
    external_action: ExternalActionPort,
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
