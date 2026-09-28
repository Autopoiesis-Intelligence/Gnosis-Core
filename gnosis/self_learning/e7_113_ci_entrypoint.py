"""E7.113 real GitHub-runner integration entrypoint.

Builds frozen selection/scope from the workflow's actual commit/ref and runs
the fail-closed bounded proof. No synthetic PASS or fabricated target state.
"""
from __future__ import annotations

import json
import os
from dataclasses import asdict, is_dataclass
from enum import Enum
from pathlib import Path

from gnosis.self_learning.e7_106_selection import (
    CandidateRecord,
    SelectionStatus,
    create_selection_record,
)
from gnosis.self_learning.e7_113_execute_bounded_proof import run_bounded_proof
from gnosis.self_learning.e7_114_scope_lock import create_scope_lock


def _serialize(value):
    if is_dataclass(value):
        return {k: _serialize(v) for k, v in asdict(value).items()}
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, tuple):
        return [_serialize(v) for v in value]
    if isinstance(value, dict):
        return {k: _serialize(v) for k, v in value.items()}
    return value


def main() -> int:
    root = Path.cwd()
    sha = os.environ["GITHUB_SHA"].lower()
    ref = os.environ["GITHUB_REF"]
    repository = os.environ["GITHUB_REPOSITORY"]
    run_id = os.environ.get("E7_RUN_ID", f"e7-113-{os.environ.get('GITHUB_RUN_ID', 'local')}")
    artifact_dir = root / "artifacts" / "e7-113"
    artifact_dir.mkdir(parents=True, exist_ok=True)

    candidate = CandidateRecord(
        candidate_id="E7.113-REAL-RUNNER",
        contract_id="E7.113",
        revision="runtime-integration-1",
        current_status="READY_FOR_BOUNDED_RUNTIME_PROOF",
        dependency_status="E7.106-E7.112",
        implementation_paths=(
            "gnosis/self_learning/e7_113_execute_bounded_proof.py",
        ),
        acceptance_criteria_count=1,
        mapped_test_count=2,
        runtime_proof_requirements=("real GitHub runner command",),
        existing_evidence_ids=(),
        evidence_commits=(sha,),
        known_gaps=(),
        trust_boundary_relevance="real execution must derive evidence without caller-supplied PASS",
        execution_prerequisites=("python", "pytest"),
        selection_status=SelectionStatus.SELECTED,
        selection_rationale="Selected from the actual workflow target at GITHUB_SHA.",
    )

    selection = create_selection_record(
        selection_record_id=f"{run_id}:selection",
        batch_id=run_id,
        baseline_id=sha,
        repository=repository,
        target_commit_sha=sha,
        candidates=(candidate,),
        selected_candidate_ids=(candidate.candidate_id,),
        reserve_candidate_ids=(),
        excluded_candidate_ids=(),
        blocked_candidate_ids=(),
        runtime_scenarios=("real-runner-evidence-chain",),
        evidence_capture_points=("returncode", "stdout", "stderr"),
        stop_conditions=("preflight failure", "audit rejection", "closure verification failure"),
        selection_policy_revision="E7.106-runtime-integration-1",
    )

    scope = create_scope_lock(
        batch_id=run_id,
        selection_record_id=selection.selection_record_id,
        selection_record_digest=selection.integrity_digest,
        scope_lock_id=f"{run_id}:scope",
        repository=repository,
        branch_ref=ref,
        target_commit_sha=sha,
        contract_ids=("E7.113",),
        criterion_ids=("E7.113.REAL-RUNNER",),
        implementation_paths=selection.candidates[0].implementation_paths,
        runtime_paths=(
            "tests/test_e7_111_independent_audit.py",
            "tests/test_e7_112_immutable_closure.py",
            "tests/test_e7_113_execute_bounded_proof.py",
        ),
        commands=("pytest -q tests/test_e7_111_independent_audit.py tests/test_e7_112_immutable_closure.py tests/test_e7_113_execute_bounded_proof.py",),
        expected_outcomes=("pytest exits successfully",),
        evidence_destinations=("artifacts/e7-113",),
        environment_prerequisites=("python", "pytest"),
        stop_conditions=selection.stop_conditions,
        evidence_policy_revision="E7.108-runtime-evidence-1",
        verification_matrix_revision="E7.111-independent-audit-1",
        progress_policy_revision="E7.113-no-mutation-1",
    )

    result = run_bounded_proof(
        run_id=run_id,
        scope_lock=scope,
        selection_record=selection,
        repository_root=root,
        resolved_commit_sha=sha,
        resolved_branch_ref=ref,
    )

    artifact = _serialize(result)
    output = root / "artifacts" / "e7-113" / "proof-run-evidence.json"
    output.write_text(json.dumps(artifact, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(output)
    return 0 if result.proof_run.state.value == "PASSED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
