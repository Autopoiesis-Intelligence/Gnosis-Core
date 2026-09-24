"""Fail-closed external execution evidence and reconciliation boundary (E7.77)."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Mapping

_RESULT_STATES = {
    "NOT_ATTEMPTED", "ATTEMPTED", "SUCCEEDED", "FAILED",
    "PARTIAL", "UNKNOWN", "REJECTED_BY_BOUNDARY",
}
_RECONCILIATION_STATES = {"RECONCILED", "MISMATCH", "INCOMPLETE", "UNKNOWN", "REJECTED"}
_SHAREABLE = {"SHAREABLE_ABSTRACTION", "PUBLIC_APPROVED"}


def _digest(fields: Mapping[str, object]) -> str:
    return "sha256:" + hashlib.sha256(
        json.dumps(fields, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


@dataclass(frozen=True)
class ExecutionEvidence:
    evidence_id: str
    authorization_id: str
    authorization_digest: str
    review_id: str
    review_digest: str
    proposal_id: str
    proposal_revision: str
    action_class: str
    target_resource: str
    authorized_scope: str
    executor_id: str
    execution_attempt_id: str
    execution_order: str
    result_status: str
    target_before_revision: str
    target_after_revision: str
    privacy_classification: str
    reconciliation_status: str
    provenance_refs: tuple[str, ...]
    observed_scope: str
    expected_preconditions: tuple[str, ...]
    evidence_digest: str

    def __post_init__(self) -> None:
        if self.result_status not in _RESULT_STATES:
            raise ValueError("unsupported result state")
        if self.reconciliation_status not in _RECONCILIATION_STATES:
            raise ValueError("unsupported reconciliation state")
        required = (
            self.authorization_id, self.authorization_digest, self.review_id,
            self.review_digest, self.proposal_id, self.proposal_revision,
            self.action_class, self.target_resource, self.authorized_scope,
            self.executor_id, self.execution_attempt_id, self.execution_order,
            self.privacy_classification, self.observed_scope, self.evidence_digest,
        )
        if not all(v.strip() for v in required):
            raise ValueError("required evidence fields are missing")
        if self.privacy_classification not in _SHAREABLE:
            raise ValueError("evidence requires explicit shareable classification")
        canonical = {
            "authorization_id": self.authorization_id,
            "authorization_digest": self.authorization_digest,
            "review_id": self.review_id,
            "review_digest": self.review_digest,
            "proposal_id": self.proposal_id,
            "proposal_revision": self.proposal_revision,
            "action_class": self.action_class,
            "target_resource": self.target_resource,
            "authorized_scope": self.authorized_scope,
            "executor_id": self.executor_id,
            "execution_attempt_id": self.execution_attempt_id,
            "execution_order": self.execution_order,
            "result_status": self.result_status,
            "target_before_revision": self.target_before_revision,
            "target_after_revision": self.target_after_revision,
            "privacy_classification": self.privacy_classification,
            "reconciliation_status": self.reconciliation_status,
            "provenance_refs": self.provenance_refs,
            "observed_scope": self.observed_scope,
            "expected_preconditions": self.expected_preconditions,
        }
        if self.evidence_digest != _digest(canonical):
            raise ValueError("evidence digest does not match canonical content")


def record_execution_evidence(
    *,
    authorization_id: str,
    authorization_digest: str,
    review_id: str,
    review_digest: str,
    proposal_id: str,
    proposal_revision: str,
    action_class: str,
    target_resource: str,
    authorized_scope: str,
    executor_id: str,
    execution_attempt_id: str,
    execution_order: str,
    result_status: str,
    target_before_revision: str = "",
    target_after_revision: str = "",
    privacy_classification: str,
    observed_scope: str,
    expected_preconditions: tuple[str, ...],
    provenance_refs: tuple[str, ...],
    authorization_valid: bool = True,
    linkage_valid: bool = True,
    target_matches: bool = True,
    scope_matches: bool = True,
    result_evidence_sufficient: bool = True,
    privacy_matches: bool = True,
    before_after_consistent: bool = True,
    duplicate_conflict: bool = False,
) -> ExecutionEvidence:
    if result_status not in _RESULT_STATES:
        raise ValueError("unsupported result state")
    if duplicate_conflict:
        raise ValueError("conflicting execution observation")
    if not all((authorization_valid, linkage_valid, target_matches, scope_matches,
                result_evidence_sufficient, privacy_matches, before_after_consistent)):
        reconciliation = "REJECTED"
    elif result_status == "SUCCEEDED":
        reconciliation = "RECONCILED"
    elif result_status in {"FAILED", "PARTIAL"}:
        reconciliation = "INCOMPLETE"
    elif result_status == "UNKNOWN":
        reconciliation = "UNKNOWN"
    elif result_status == "NOT_ATTEMPTED":
        reconciliation = "INCOMPLETE"
    else:
        reconciliation = "REJECTED"
    fields = {
        "authorization_id": authorization_id,
        "authorization_digest": authorization_digest,
        "review_id": review_id,
        "review_digest": review_digest,
        "proposal_id": proposal_id,
        "proposal_revision": proposal_revision,
        "action_class": action_class,
        "target_resource": target_resource,
        "authorized_scope": authorized_scope,
        "executor_id": executor_id,
        "execution_attempt_id": execution_attempt_id,
        "execution_order": execution_order,
        "result_status": result_status,
        "target_before_revision": target_before_revision,
        "target_after_revision": target_after_revision,
        "privacy_classification": privacy_classification,
        "reconciliation_status": reconciliation,
        "provenance_refs": provenance_refs,
        "observed_scope": observed_scope,
        "expected_preconditions": expected_preconditions,
    }
    return ExecutionEvidence(
        evidence_id=_digest(fields),
        **fields,
        evidence_digest=_digest(fields),
    )


def validate_observation_against_authorization(
    *,
    evidence: ExecutionEvidence,
    authorization_id: str,
    authorization_digest: str,
    review_id: str,
    review_digest: str,
    proposal_id: str,
    proposal_revision: str,
    action_class: str,
    target_resource: str,
    authorized_scope: str,
    observed_scope: str,
    execution_attempt_id: str,
    result_status: str,
) -> bool:
    if evidence.reconciliation_status != "RECONCILED":
        return False
    return all((
        evidence.authorization_id == authorization_id,
        evidence.authorization_digest == authorization_digest,
        evidence.review_id == review_id,
        evidence.review_digest == review_digest,
        evidence.proposal_id == proposal_id,
        evidence.proposal_revision == proposal_revision,
        evidence.action_class == action_class,
        evidence.target_resource == target_resource,
        evidence.authorized_scope == authorized_scope,
        evidence.observed_scope == observed_scope,
        evidence.execution_attempt_id == execution_attempt_id,
        evidence.result_status == result_status == "SUCCEEDED",
    ))
