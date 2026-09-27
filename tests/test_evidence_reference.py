import hashlib
import sqlite3

import pytest

from gnosis.storage import (
    EvidenceReference,
    StorageCorruptionError,
    SecretMaterialError,
    connect,
    evidence_id_for,
    load_evidence_reference,
    save_evidence_reference,
)


def _digest(value: bytes = b"ci evidence") -> str:
    return hashlib.sha256(value).hexdigest()


def _reference(**overrides) -> EvidenceReference:
    values = {
        "evidence_type": "ci-test-result",
        "producer": "github-actions",
        "created_at": "2026-09-27T20:00:00Z",
        "source_ref": "run:123/job:456/artifact:789",
        "content_digest": _digest(),
        "scope": "e7.108",
        "status": "observed",
        "related_task_id": "R2-CONTRACT-15",
        "related_checkpoint_id": "r2.3.7",
        "baseline_commit": "beb8463410865bcaff8f4c48440b5311b56e0d6a",
        "test_command": "pytest tests/test_e7_108_execution_record.py",
    }
    values.update(overrides)
    identity = evidence_id_for(
        evidence_type=values["evidence_type"],
        producer=values["producer"],
        source_ref=values["source_ref"],
        content_digest=values["content_digest"],
        scope=values["scope"],
        related_task_id=values["related_task_id"],
        related_checkpoint_id=values["related_checkpoint_id"],
        baseline_commit=values["baseline_commit"],
        test_command=values["test_command"],
    )
    values["evidence_id"] = identity
    return EvidenceReference(**values)


def test_evidence_reference_round_trip_and_stable_identity():
    conn = connect()
    reference = _reference()
    save_evidence_reference(conn, reference)
    assert load_evidence_reference(conn, reference.evidence_id) == reference
    assert reference.evidence_id == evidence_id_for(
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


def test_duplicate_identical_evidence_is_idempotent():
    conn = connect()
    reference = _reference()
    save_evidence_reference(conn, reference)
    save_evidence_reference(conn, reference)
    assert conn.execute("SELECT count(*) FROM evidence_references").fetchone()[0] == 1


def test_conflicting_replay_fails_closed():
    conn = connect()
    reference = _reference()
    save_evidence_reference(conn, reference)
    conflicting = _reference(status="reproducible")
    conflicting = EvidenceReference(
        evidence_id=reference.evidence_id,
        evidence_type=conflicting.evidence_type,
        producer=conflicting.producer,
        created_at=reference.created_at,
        source_ref=reference.source_ref,
        content_digest=reference.content_digest,
        scope=reference.scope,
        status=conflicting.status,
        related_task_id=reference.related_task_id,
        related_checkpoint_id=reference.related_checkpoint_id,
        baseline_commit=reference.baseline_commit,
        test_command=reference.test_command,
    )
    with pytest.raises(StorageCorruptionError, match="conflicting evidence replay"):
        save_evidence_reference(conn, conflicting)


def test_identity_changes_when_content_or_baseline_changes():
    base = _reference()
    assert _reference(content_digest=_digest(b"changed")).evidence_id != base.evidence_id
    assert _reference(baseline_commit="edfcb3ee20a2f52ecd3915eb845f33d16d8f6476").evidence_id != base.evidence_id


def test_tampered_persisted_reference_fails_closed():
    conn = connect()
    reference = _reference()
    save_evidence_reference(conn, reference)
    conn.execute("DROP TRIGGER evidence_references_no_update")
    conn.execute(
        "UPDATE evidence_references SET source_ref='tampered' WHERE evidence_id=?",
        (reference.evidence_id,),
    )
    with pytest.raises(StorageCorruptionError, match="evidence identity mismatch"):
        load_evidence_reference(conn, reference.evidence_id)


def test_evidence_reference_is_append_only():
    conn = connect()
    reference = _reference()
    save_evidence_reference(conn, reference)
    with pytest.raises(sqlite3.DatabaseError):
        conn.execute(
            "UPDATE evidence_references SET status='reproducible' WHERE evidence_id=?",
            (reference.evidence_id,),
        )
    with pytest.raises(sqlite3.DatabaseError):
        conn.execute(
            "DELETE FROM evidence_references WHERE evidence_id=?",
            (reference.evidence_id,),
        )


@pytest.mark.parametrize("digest", ["", "ABC", "g" * 64, "a" * 63])
def test_invalid_content_digest_rejected(digest):
    with pytest.raises(ValueError, match="content_digest"):
        evidence_id_for(
            evidence_type="ci",
            producer="test",
            source_ref="run:1",
            content_digest=digest,
            scope="test",
        )


def test_secret_bearing_reference_is_rejected():
    with pytest.raises(SecretMaterialError):
        evidence_id_for(
            evidence_type="ci",
            producer="github-actions",
            source_ref="https://example.invalid/run?token=secret",
            content_digest=_digest(),
            scope="test",
        )


def test_schema_version_is_six_and_evidence_table_exists():
    conn = connect()
    assert conn.execute("SELECT value FROM schema_meta WHERE key='schema_version'").fetchone()[0] == "6"
    assert conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='evidence_references'"
    ).fetchone()[0] == "evidence_references"
