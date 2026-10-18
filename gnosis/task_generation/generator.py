"""Generate non-authoritative engineering task candidates from structured findings.

This module is intentionally deterministic and standard-library-only. It does not
execute tasks, access external sources, mutate Core state, or grant authority.
"""
from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from typing import Any

GENERATOR_ID = "gnosis.local_engineering_task_generator"
GENERATOR_VERSION = "1"


class TaskGenerationError(ValueError):
    """Raised when a source finding lacks explicit, testable task information."""


def _required_text(source: Mapping[str, Any], field: str) -> str:
    value = source.get(field)
    if not isinstance(value, str) or not value.strip():
        raise TaskGenerationError(f"{field} must be a non-empty string")
    return value.strip()


def _string_list(source: Mapping[str, Any], field: str) -> list[str]:
    value = source.get(field)
    if not isinstance(value, (list, tuple)) or not value:
        raise TaskGenerationError(f"{field} must be a non-empty list of strings")
    if any(not isinstance(item, str) or not item.strip() for item in value):
        raise TaskGenerationError(f"{field} must contain only non-empty strings")
    # Stable de-duplication preserves source order and avoids accidental expansion.
    return list(dict.fromkeys(item.strip() for item in value))


def generate_task_candidate(
    source: Mapping[str, Any],
    *,
    source_revision: str,
    allowed_scope: Sequence[str],
    forbidden_scope: Sequence[str],
) -> dict[str, Any]:
    """Create a deterministic PROPOSED task from a structured engineering finding.

    Required source keys:
      finding_id, title, observation, recommended_action, acceptance_criteria,
      evidence_required, source_refs

    Scope must be supplied explicitly by the caller. The output is a proposal,
    never an execution authorization or a claim that implementation is verified.
    """
    if not isinstance(source, Mapping):
        raise TaskGenerationError("source must be a mapping")
    if not isinstance(source_revision, str) or not source_revision.strip():
        raise TaskGenerationError("source_revision must be a non-empty string")

    finding_id = _required_text(source, "finding_id")
    title = _required_text(source, "title")
    observation = _required_text(source, "observation")
    recommended_action = _required_text(source, "recommended_action")
    acceptance_criteria = _string_list(source, "acceptance_criteria")
    evidence_required = _string_list(source, "evidence_required")
    source_refs = _string_list(source, "source_refs")

    if not isinstance(allowed_scope, (list, tuple)) or not allowed_scope:
        raise TaskGenerationError("allowed_scope must be a non-empty list")
    if not isinstance(forbidden_scope, (list, tuple)) or not forbidden_scope:
        raise TaskGenerationError("forbidden_scope must be a non-empty list")
    if any(not isinstance(item, str) or not item.strip() for item in (*allowed_scope, *forbidden_scope)):
        raise TaskGenerationError("scope entries must be non-empty strings")

    normalized_scope = {
        "allowed": list(dict.fromkeys(item.strip() for item in allowed_scope)),
        "forbidden": list(dict.fromkeys(item.strip() for item in forbidden_scope)),
    }
    if set(normalized_scope["allowed"]) & set(normalized_scope["forbidden"]):
        raise TaskGenerationError("allowed_scope and forbidden_scope must not overlap")

    identity_material = {
        "generator_id": GENERATOR_ID,
        "generator_version": GENERATOR_VERSION,
        "finding_id": finding_id,
        "source_revision": source_revision.strip(),
        "title": title,
        "observation": observation,
        "recommended_action": recommended_action,
        "acceptance_criteria": acceptance_criteria,
        "evidence_required": evidence_required,
        "source_refs": source_refs,
        "scope": normalized_scope,
    }
    canonical = json.dumps(identity_material, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    task_id = "task-" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:20]

    return {
        "schema": "gnosis.engineering-task-candidate/v1",
        "task_id": task_id,
        "status": "PROPOSED",
        "objective": recommended_action,
        "title": title,
        "source_finding": {
            "finding_id": finding_id,
            "observation": observation,
            "source_refs": source_refs,
            "source_revision": source_revision.strip(),
        },
        "scope": normalized_scope,
        "acceptance_criteria": acceptance_criteria,
        "evidence_required": evidence_required,
        "provenance": {
            "generator_id": GENERATOR_ID,
            "generator_version": GENERATOR_VERSION,
            "identity_sha256": hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
        },
        "authority": {
            "may_execute": False,
            "may_modify_core": False,
            "may_mark_verified": False,
            "requires_independent_validation": True,
        },
        "implementation_state": "NOT_STARTED",
        "verification_state": "NOT_VERIFIED",
    }
