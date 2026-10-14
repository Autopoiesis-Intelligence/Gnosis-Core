"""Independent durable evaluation and governance evidence records.

These records preserve evaluator/governance outputs separately from the aggregate
EvidenceProvenance. They are evidence, not execution authority. The caller owns
the SQLite transaction; these functions never commit it.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import asdict
from typing import Any

from gnosis.evolution.evaluator import EvaluationResult, EvaluatorIdentity
from gnosis.reflection.governance import GovernanceDecision


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _record_id(kind: str, execution_id: str, candidate_id: str, evidence_digest: str, payload: dict[str, Any]) -> str:
    body = {
        "kind": kind,
        "execution_id": execution_id,
        "candidate_id": candidate_id,
        "evidence_digest": evidence_digest,
        "payload": payload,
    }
    return kind + ":" + hashlib.sha256(_canonical(body).encode("utf-8")).hexdigest()[:32]


def ensure_evolution_decision_evidence_schema(conn: sqlite3.Connection) -> None:
    conn.execute(
        """CREATE TABLE IF NOT EXISTS evolution_decision_evidence (
            record_id TEXT PRIMARY KEY,
            kind TEXT NOT NULL CHECK(kind IN ('evaluation', 'governance')),
            execution_id TEXT NOT NULL,
            candidate_id TEXT NOT NULL,
            evidence_digest TEXT NOT NULL,
            payload TEXT NOT NULL
        )"""
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_evolution_decision_evidence_execution "
        "ON evolution_decision_evidence(execution_id, kind)"
    )


def persist_decision_evidence(
    conn: sqlite3.Connection,
    *,
    execution_id: str,
    candidate_id: str,
    evidence_digest: str,
    evaluation: EvaluationResult,
    governance: GovernanceDecision,
) -> tuple[str, str]:
    """Persist evaluation and governance independently without committing the caller's transaction."""
    if not execution_id or not candidate_id or not evidence_digest:
        raise ValueError("decision evidence requires execution, candidate and evidence digest")
    if evaluation.evidence_digest != evidence_digest:
        raise ValueError("evaluation evidence digest does not match execution evidence")
    ensure_evolution_decision_evidence_schema(conn)
    evaluation_payload = {
        "status": evaluation.status,
        "rationale": list(evaluation.rationale),
        "evidence_digest": evaluation.evidence_digest,
        "evaluator_identity": asdict(evaluation.evaluator_identity),
    }
    governance_payload = {
        "decision": governance.decision,
        "shadow_status": governance.shadow_status,
        "invariant_status": governance.invariant_status,
        "rationale": list(governance.rationale),
        "provenance": governance.provenance,
    }
    ids = (
        _record_id("evaluation", execution_id, candidate_id, evidence_digest, evaluation_payload),
        _record_id("governance", execution_id, candidate_id, evidence_digest, governance_payload),
    )
    rows = (
        (ids[0], "evaluation", execution_id, candidate_id, evidence_digest, _canonical(evaluation_payload)),
        (ids[1], "governance", execution_id, candidate_id, evidence_digest, _canonical(governance_payload)),
    )
    for row in rows:
        existing = conn.execute(
            "SELECT record_id,kind,execution_id,candidate_id,evidence_digest,payload "
            "FROM evolution_decision_evidence WHERE record_id=?",
            (row[0],),
        ).fetchone()
        if existing is not None:
            if tuple(existing) != row:
                raise RuntimeError("conflicting decision evidence replay")
            continue
        conn.execute(
            "INSERT INTO evolution_decision_evidence "
            "(record_id,kind,execution_id,candidate_id,evidence_digest,payload) VALUES (?,?,?,?,?,?)",
            row,
        )
    return ids


def load_decision_evidence(
    conn: sqlite3.Connection,
    *,
    evaluation_record_id: str,
    governance_record_id: str,
    execution_id: str,
    candidate_id: str,
    evidence_digest: str,
) -> tuple[EvaluationResult, GovernanceDecision]:
    """Reload and verify separately persisted evaluation and governance records."""
    ensure_evolution_decision_evidence_schema(conn)

    def load(record_id: str, kind: str) -> dict[str, Any]:
        row = conn.execute(
            "SELECT record_id,kind,execution_id,candidate_id,evidence_digest,payload "
            "FROM evolution_decision_evidence WHERE record_id=?",
            (record_id,),
        ).fetchone()
        if row is None:
            raise KeyError(record_id)
        if row[1] != kind or row[2] != execution_id or row[3] != candidate_id or row[4] != evidence_digest:
            raise RuntimeError(f"{kind} evidence binding mismatch")
        try:
            payload = json.loads(row[5])
        except (TypeError, ValueError) as exc:
            raise RuntimeError(f"{kind} evidence payload malformed") from exc
        if _record_id(kind, execution_id, candidate_id, evidence_digest, payload) != record_id:
            raise RuntimeError(f"{kind} evidence integrity mismatch")
        return payload

    ep = load(evaluation_record_id, "evaluation")
    gp = load(governance_record_id, "governance")
    try:
        evaluation = EvaluationResult(
            status=ep["status"],
            rationale=tuple(ep["rationale"]),
            evidence_digest=ep["evidence_digest"],
            evaluator_identity=EvaluatorIdentity(**ep["evaluator_identity"]),
        )
        governance = GovernanceDecision(
            decision=gp["decision"],
            shadow_status=gp["shadow_status"],
            invariant_status=gp["invariant_status"],
            rationale=tuple(gp["rationale"]),
            provenance=gp["provenance"],
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise RuntimeError("decision evidence payload malformed") from exc
    if evaluation.evidence_digest != evidence_digest:
        raise RuntimeError("evaluation evidence digest mismatch")
    return evaluation, governance
