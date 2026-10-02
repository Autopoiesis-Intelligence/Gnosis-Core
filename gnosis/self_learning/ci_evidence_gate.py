"""Fail-closed CI evidence contract for self-learning (E7.60)."""
from __future__ import annotations
import hashlib
import json
from dataclasses import dataclass

VALID_RESULTS = {"PASS", "FAIL"}
VALID_STATUSES = {"OBSERVED", "UNVERIFIED", "REJECTED"}

@dataclass(frozen=True)
class CIEvidence:
    evidence_id: str
    commit_sha: str
    workflow_run_id: str
    job_id: str
    scope: str
    execution_observed: bool
    result: str
    evidence_digest: str
    status: str

def create_ci_evidence(*, commit_sha, workflow_run_id, job_id, scope,
                       execution_observed, result, evidence_digest,
                       status="UNVERIFIED"):
    if not all(x.strip() for x in (commit_sha, workflow_run_id, job_id, scope, evidence_digest)):
        raise ValueError("CI evidence identity is required")
    if result not in VALID_RESULTS:
        raise ValueError("invalid CI result")
    if status not in VALID_STATUSES:
        raise ValueError("invalid CI evidence status")
    if not execution_observed and status == "OBSERVED":
        raise ValueError("unobserved CI execution cannot be observed")
    if execution_observed and status == "UNVERIFIED":
        raise ValueError("observed CI execution requires an observed status")
    payload = dict(commit_sha=commit_sha, workflow_run_id=workflow_run_id,
                   job_id=job_id, scope=scope,
                   execution_observed=execution_observed, result=result,
                   evidence_digest=evidence_digest, status=status)
    evidence_id = "sha256:" + hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return CIEvidence(evidence_id=evidence_id, **payload)

def may_prove_ci(*, evidence, expected_commit_sha, expected_scope):
    if evidence.status != "OBSERVED":
        return False
    if not evidence.execution_observed:
        return False
    if evidence.commit_sha != expected_commit_sha:
        return False
    if evidence.scope != expected_scope:
        return False
    return True

def may_admit_learning(*, evidence, expected_commit_sha, expected_scope):
    return may_prove_ci(
        evidence=evidence,
        expected_commit_sha=expected_commit_sha,
        expected_scope=expected_scope,
    ) and evidence.result == "PASS"

def creates_execution_authority(*, evidence):
    return False
