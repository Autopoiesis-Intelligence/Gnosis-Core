"""Fail-closed collaboration execution authorization boundary (E7.76).

This module issues deterministic authorization records only. It never executes
external actions, mutates Core, or treats execution evidence as authority.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable, Mapping

_ALLOWED_ACTIONS = {
    "PUBLISH_PUBLIC",
    "CREATE_PUBLIC_ISSUE_OR_PR",
    "CREATE_PARTNER_PACKAGE",
    "SEND_INVITATION",
    "UPDATE_PUBLIC_REPOSITORY_METADATA",
}
_DECISIONS = {"ALLOW", "DENY"}
_SHAREABLE = {"SHAREABLE_ABSTRACTION", "PUBLIC_APPROVED"}
_UNKNOWN = {"UNKNOWN", ""}
_TRUSTED_EVIDENCE_SOURCES = {"trusted-review-engine"}


def _canonical_timestamp(value: str) -> str:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("timestamp must be ISO-8601") from exc
    if parsed.tzinfo is None or parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        raise ValueError("timestamp must use UTC timezone")
    canonical = parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    if value != canonical:
        raise ValueError("timestamp must use canonical UTC ISO-8601 form")
    return canonical


def _digest(fields: Mapping[str, object]) -> str:
    return "sha256:" + hashlib.sha256(
        json.dumps(fields, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


@dataclass(frozen=True)
class PreconditionEvidence:
    source_id: str
    target_revision: str
    evidence_revision: str
    observed_conditions: tuple[str, ...]
    provenance: str

    @property
    def digest(self) -> str:
        return _digest(
            {
                "source_id": self.source_id,
                "target_revision": self.target_revision,
                "evidence_revision": self.evidence_revision,
                "observed_conditions": self.observed_conditions,
                "provenance": self.provenance,
            }
        )

    def __post_init__(self) -> None:
        required = (
            self.source_id,
            self.target_revision,
            self.evidence_revision,
            self.provenance,
        )
        if not all(value.strip() for value in required):
            raise ValueError("evidence identity fields are required")
        if self.source_id not in _TRUSTED_EVIDENCE_SOURCES:
            raise ValueError("evidence source is not trusted")


TrustedEvidenceResolver = Callable[[str], PreconditionEvidence | None]
TargetRevisionResolver = Callable[[str], str | None]


@dataclass(frozen=True)
class ExecutionAuthorization:
    authorization_id: str
    review_id: str
    review_digest: str
    proposal_id: str
    proposal_revision: str
    action_class: str
    target_resource: str
    authorized_scope: str
    executor_id: str
    authorization_basis: str
    privacy_classification: str
    issuance_revision: str
    expires_at: str
    revocation_revision: str | None
    preconditions: tuple[str, ...]
    precondition_evidence_digest: str
    authorized_target_revision: str
    decision: str
    status: str
    authority: str = "execution-authorization-only"

    def __post_init__(self) -> None:
        if self.decision not in _DECISIONS or self.status != self.decision:
            raise ValueError("invalid authorization decision/status")
        required = (
            self.review_id,
            self.review_digest,
            self.proposal_id,
            self.proposal_revision,
            self.action_class,
            self.target_resource,
            self.authorized_scope,
            self.executor_id,
            self.authorization_basis,
            self.privacy_classification,
            self.issuance_revision,
            self.expires_at,
        )
        if not all(value.strip() for value in required):
            raise ValueError("authorization identity fields are required")
        if self.action_class not in _ALLOWED_ACTIONS:
            raise ValueError("unsupported action class")
        if self.authority != "execution-authorization-only":
            raise ValueError("authorization cannot self-promote")
        canonical = {
            "review_id": self.review_id,
            "review_digest": self.review_digest,
            "proposal_id": self.proposal_id,
            "proposal_revision": self.proposal_revision,
            "action_class": self.action_class,
            "target_resource": self.target_resource,
            "authorized_scope": self.authorized_scope,
            "executor_id": self.executor_id,
            "authorization_basis": self.authorization_basis,
            "privacy_classification": self.privacy_classification,
            "issuance_revision": self.issuance_revision,
            "expires_at": self.expires_at,
            "revocation_revision": self.revocation_revision,
            "preconditions": self.preconditions,
            "precondition_evidence_digest": self.precondition_evidence_digest,
            "authorized_target_revision": self.authorized_target_revision,
            "decision": self.decision,
            "status": self.status,
        }
        if self.authorization_id != _digest(canonical):
            raise ValueError("authorization identity does not match canonical content")


def _accepted_review(
    *,
    review_id: str,
    review_digest: str,
    review_decision: str,
    review_proposal_id: str,
    review_proposal_revision: str,
    proposal_id: str,
    proposal_revision: str,
) -> bool:
    return (
        review_decision == "ACCEPTED"
        and review_id.strip()
        and review_digest.strip()
        and review_proposal_id == proposal_id
        and review_proposal_revision == proposal_revision
    )


def issue_execution_authorization(
    *,
    review_id: str,
    review_digest: str,
    review_decision: str,
    review_proposal_id: str,
    review_proposal_revision: str,
    proposal_id: str,
    proposal_revision: str,
    action_class: str,
    target_resource: str,
    authorized_scope: str,
    executor_id: str,
    authorization_basis: str,
    privacy_classification: str,
    issuance_revision: str,
    expires_at: str,
    preconditions: tuple[str, ...],
    authorized_target_revision: str,
    precondition_evidence: PreconditionEvidence | None = None,
    required_preconditions_present: bool = True,
    revoked: bool = False,
    stale: bool = False,
    scope_allowed: bool = True,
    provenance_complete: bool = True,
) -> ExecutionAuthorization:
    if action_class not in _ALLOWED_ACTIONS:
        raise ValueError("unsupported action class")
    if not _accepted_review(
        review_id=review_id,
        review_digest=review_digest,
        review_decision=review_decision,
        review_proposal_id=review_proposal_id,
        review_proposal_revision=review_proposal_revision,
        proposal_id=proposal_id,
        proposal_revision=proposal_revision,
    ):
        raise ValueError("authorization requires exact ACCEPTED review binding")
    if privacy_classification in _UNKNOWN or privacy_classification not in _SHAREABLE:
        raise ValueError("authorization requires explicit shareable privacy classification")
    if not all(x.strip() for x in (target_resource, authorized_scope, executor_id, authorization_basis, issuance_revision, expires_at, authorized_target_revision)):
        raise ValueError("authorization scope and identity fields are required")
    _canonical_timestamp(expires_at)
    if precondition_evidence is None:
        raise ValueError("trusted precondition evidence is required")
    if precondition_evidence.target_revision != authorized_target_revision:
        raise ValueError("precondition evidence target does not match authorization target")
    if not set(preconditions).issubset(set(precondition_evidence.observed_conditions)):
        raise ValueError("precondition evidence does not satisfy declared conditions")
    precondition_evidence_digest = precondition_evidence.digest
    if revoked or stale or not scope_allowed or not provenance_complete or not required_preconditions_present:
        raise ValueError("authorization preconditions are not satisfied")
    fields = {
        "review_id": review_id,
        "review_digest": review_digest,
        "proposal_id": proposal_id,
        "proposal_revision": proposal_revision,
        "action_class": action_class,
        "target_resource": target_resource,
        "authorized_scope": authorized_scope,
        "executor_id": executor_id,
        "authorization_basis": authorization_basis,
        "privacy_classification": privacy_classification,
        "issuance_revision": issuance_revision,
        "expires_at": expires_at,
        "revocation_revision": None,
        "preconditions": preconditions,
        "precondition_evidence_digest": precondition_evidence_digest,
        "authorized_target_revision": authorized_target_revision,
        "decision": "ALLOW",
        "status": "ALLOW",
    }
    return ExecutionAuthorization(_digest(fields), **fields)


def validate_execution_request(
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
    target_revision_resolver: TargetRevisionResolver,
    evidence_resolver: TrustedEvidenceResolver,
    now: str,
    current_revocation_revision: str | None = None,
) -> bool:
    if authorization.decision != "ALLOW" or authorization.status != "ALLOW":
        return False
    if authorization.review_id != review_id or authorization.review_digest != review_digest:
        return False
    if authorization.proposal_id != proposal_id or authorization.proposal_revision != proposal_revision:
        return False
    if authorization.action_class != action_class or authorization.target_resource != target_resource:
        return False
    if authorization.authorized_scope != requested_scope or authorization.executor_id != executor_id:
        return False
    if authorization.privacy_classification != privacy_classification:
        return False
    if authorization.privacy_classification not in _SHAREABLE:
        return False
    if current_revocation_revision is not None:
        return False
    if authorization.revocation_revision is not None:
        return False
    try:
        now_canonical = _canonical_timestamp(now)
    except ValueError:
        return False
    if now_canonical >= authorization.expires_at:
        return False
    try:
        live_target_revision = target_revision_resolver(authorization.target_resource)
        live_evidence = evidence_resolver(authorization.precondition_evidence_digest)
    except Exception:
        return False
    if live_target_revision != authorization.authorized_target_revision:
        return False
    if live_evidence is None:
        return False
    if live_evidence.target_revision != live_target_revision:
        return False
    if live_evidence.digest != authorization.precondition_evidence_digest:
        return False
    if not set(authorization.preconditions).issubset(set(live_evidence.observed_conditions)):
        return False
    return True


def revoke_execution_authorization(
    authorization: ExecutionAuthorization, *, revocation_revision: str
) -> ExecutionAuthorization:
    if not revocation_revision.strip():
        raise ValueError("revocation revision is required")
    fields = {
        "review_id": authorization.review_id,
        "review_digest": authorization.review_digest,
        "proposal_id": authorization.proposal_id,
        "proposal_revision": authorization.proposal_revision,
        "action_class": authorization.action_class,
        "target_resource": authorization.target_resource,
        "authorized_scope": authorization.authorized_scope,
        "executor_id": authorization.executor_id,
        "authorization_basis": authorization.authorization_basis,
        "privacy_classification": authorization.privacy_classification,
        "issuance_revision": authorization.issuance_revision,
        "expires_at": authorization.expires_at,
        "revocation_revision": revocation_revision,
        "preconditions": authorization.preconditions,
        "precondition_evidence_digest": authorization.precondition_evidence_digest,
        "authorized_target_revision": authorization.authorized_target_revision,
        "decision": "DENY",
        "status": "DENY",
    }
    return ExecutionAuthorization(_digest(fields), **fields)
