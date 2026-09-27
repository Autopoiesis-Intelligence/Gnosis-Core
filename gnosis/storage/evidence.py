from __future__ import annotations

import hashlib
import re
import sqlite3
from dataclasses import dataclass
from typing import Any

from .repositories import StorageCorruptionError, canonical_json, utc_now

_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_ALLOWED_STATUSES = frozenset({"observed", "reproducible", "independently_verified"})


@dataclass(frozen=True)
class EvidenceReference:
    evidence_id: str
    evidence_type: str
    producer: str
    created_at: str
    source_ref: str
    content_digest: str
    scope: str
    status: str
    related_task_id: str | None = None
    related_checkpoint_id: str | None = None
    baseline_commit: str | None = None
    test_command: str | None = None


def _identity_payload(
    *,
    evidence_type: str,
    producer: str,
    source_ref: str,
    content_digest: str,
    scope: str,
    related_task_id: str | None,
    related_checkpoint_id: str | None,
    baseline_commit: str | None,
    test_command: str | None,
) -> dict[str, Any]:
    return {
        "evidence_type": evidence_type,
        "producer": producer,
        "source_ref": source_ref,
        "content_digest": content_digest,
        "scope": scope,
        "related_task_id": related_task_id,
        "related_checkpoint_id": related_checkpoint_id,
        "baseline_commit": baseline_commit,
        "test_command": test_command,
    }


def evidence_id_for(
    *,
    evidence_type: str,
    producer: str,
    source_ref: str,
    content_digest: str,
    scope: str,
    related_task_id: str | None = None,
    related_checkpoint_id: str | None = None,
    baseline_commit: str | None = None,
    test_command: str | None = None,
) -> str:
    if not all(isinstance(value, str) and value.strip() for value in (evidence_type, producer, source_ref, scope)):
        raise ValueError("evidence type, producer, source reference, and scope are required")
    if not _DIGEST.fullmatch(content_digest):
        raise ValueError("content_digest must be a lowercase SHA-256 hex digest")
    payload = _identity_payload(
        evidence_type=evidence_type,
        producer=producer,
        source_ref=source_ref,
        content_digest=content_digest,
        scope=scope,
        related_task_id=related_task_id,
        related_checkpoint_id=related_checkpoint_id,
        baseline_commit=baseline_commit,
        test_command=test_command,
    )
    return "evidence:" + hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def _validate(reference: EvidenceReference) -> None:
    expected = evidence_id_for(
        evidence_type=reference.evidence_type,
        producer=reference.producer,
        source_ref=reference.source_ref,
        content_digest=reference.content_digest,
        scope=reference.scope,
        related_task_id=reference.related_task_id,
        related_checkpoint_id=reference.related_checkpoint_id,
        baseline_commit=reference.baseline_commit,
        test_command=reference.test_command,
    )
    if reference.evidence_id != expected:
        raise StorageCorruptionError("evidence identity mismatch")
    if reference.status not in _ALLOWED_STATUSES:
        raise ValueError("unsupported evidence status")


def save_evidence_reference(
    conn: sqlite3.Connection,
    reference: EvidenceReference,
) -> None:
    _validate(reference)
    existing = conn.execute(
        "SELECT evidence_type,producer,created_at,source_ref,content_digest,scope,status,"
        "related_task_id,related_checkpoint_id,baseline_commit,test_command "
        "FROM evidence_references WHERE evidence_id=?",
        (reference.evidence_id,),
    ).fetchone()
    expected = (
        reference.evidence_type,
        reference.producer,
        reference.created_at,
        reference.source_ref,
        reference.content_digest,
        reference.scope,
        reference.status,
        reference.related_task_id,
        reference.related_checkpoint_id,
        reference.baseline_commit,
        reference.test_command,
    )
    if existing is not None:
        if tuple(existing) != expected:
            raise StorageCorruptionError("conflicting evidence replay")
        return
    conn.execute(
        "INSERT INTO evidence_references("
        "evidence_id,evidence_type,producer,created_at,source_ref,content_digest,scope,status,"
        "related_task_id,related_checkpoint_id,baseline_commit,test_command"
        ") VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
        (reference.evidence_id, *expected),
    )


def load_evidence_reference(
    conn: sqlite3.Connection,
    evidence_id: str,
) -> EvidenceReference:
    row = conn.execute(
        "SELECT evidence_id,evidence_type,producer,created_at,source_ref,content_digest,scope,status,"
        "related_task_id,related_checkpoint_id,baseline_commit,test_command "
        "FROM evidence_references WHERE evidence_id=?",
        (evidence_id,),
    ).fetchone()
    if row is None:
        raise StorageCorruptionError(f"evidence not found: {evidence_id}")
    reference = EvidenceReference(*tuple(row))
    _validate(reference)
    return reference
