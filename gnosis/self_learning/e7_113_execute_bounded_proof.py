"""Concrete E7.113 bounded proof execution from observed stage test results."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from dataclasses import asdict
from hashlib import sha256
from pathlib import Path

from gnosis.self_learning.e7_108_execution_record import (
    CriterionEvidence,
    ExecutionRecord,
    ExecutionState,
    complete,
)
from gnosis.self_learning.e7_109_evidence_acceptance import (
    EvidenceItem,
    accept_evidence,
)
from gnosis.self_learning.e7_110_reconciliation import Metric, reconcile
from gnosis.self_learning.e7_111_independent_audit import audit_chain
from gnosis.self_learning.e7_112_immutable_closure import (
    create_closure,
    verify_closure,
)
from gnosis.self_learning.e7_113_bounded_proof_run import (
    REQUIRED_STAGES,
    complete_proof_run,
    plan_proof_run,
)

STAGE_TESTS = {
    "E7.107": "tests/test_e7_107_readiness.py",
    "E7.108": "tests/test_e7_108_execution_record.py",
    "E7.109": "tests/test_e7_109_evidence_acceptance.py",
    "E7.110": "tests/test_e7_110_reconciliation.py",
    "E7.111": "tests/test_e7_111_independent_audit.py",
    "E7.112": "tests/test_e7_112_immutable_closure.py",
}


def _actual_commit(root: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0 or not result.stdout.strip():
        raise RuntimeError("unable to resolve actual repository HEAD")
    return result.stdout.strip()


def _run_stage(stage: str, test_path: str, root: Path) -> CriterionEvidence:
    command = [sys.executable, "-m", "pytest", "-q", test_path]
    result = subprocess.run(
        command,
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    output = (result.stdout + "\n" + result.stderr).strip()
    evidence_id = sha256(
        json.dumps(
            {
                "stage": stage,
                "command": command,
                "returncode": result.returncode,
                "output": output,
            },
            sort_keys=True,
        ).encode()
    ).hexdigest()
    observed = "PASS" if result.returncode == 0 else "FAIL"
    return CriterionEvidence(
        criterion_id=stage,
        expected="PASS",
        observed=observed,
        evidence_id=evidence_id,
        passed=result.returncode == 0,
    )


def main() -> int:
    root = Path.cwd()
    run_id = os.environ.get("E7_RUN_ID", "e7-113-local")
    actual_commit = _actual_commit(root)
    declared_commit = os.environ.get("GITHUB_SHA")
    if declared_commit and declared_commit != actual_commit:
        raise RuntimeError(
            f"declared GITHUB_SHA {declared_commit} does not match checkout {actual_commit}"
        )

    commands = tuple(
        f"{sys.executable} -m pytest -q {STAGE_TESTS[stage]}"
        for stage in REQUIRED_STAGES
    )
    record = ExecutionRecord(
        run_id,
        actual_commit,
        "main",
        {"python": sys.version.split()[0], "mode": "observe-only"},
        commands,
        "SEL-BOUNDED-01",
        "BASELINE-01",
        "E7-R1",
        "E7-R1",
        (),
        ExecutionState.RUNNING,
    )

    criteria = tuple(
        _run_stage(stage, STAGE_TESTS[stage], root) for stage in REQUIRED_STAGES
    )
    record = complete(record, criteria)

    accepted = accept_evidence(
        batch_id=run_id,
        execution_record_id=run_id,
        items=tuple(
            EvidenceItem(
                c.criterion_id,
                c.evidence_id,
                c.expected,
                c.observed,
                c.passed,
            )
            for c in criteria
        ),
    )

    metrics = tuple(
        Metric(c.criterion_id, 1.0, 1.0 if c.passed else 0.0) for c in criteria
    )
    reconciliation = reconcile(
        batch_id=run_id,
        acceptance_id=run_id,
        metrics=metrics,
    )

    checks = {
        "exact_commit": record.target_commit_sha == actual_commit,
        "execution_identity": bool(record.batch_id and record.target_commit_sha),
        "evidence_completeness": (
            len(criteria) == len(REQUIRED_STAGES)
            and all(c.evidence_id for c in criteria)
        ),
        "acceptance_consistency": (
            (accepted.state.value == "ACCEPTED") == record.passed
        ),
        "reconciliation_consistency": (
            (reconciliation.state.value == "RECONCILED") == record.passed
        ),
        "no_conflicting_evidence": len(
            {c.evidence_id for c in criteria}
        ) == len(criteria),
        "terminal_state_consistency": record.terminal
        and (record.passed == all(c.passed for c in criteria)),
    }
    audit = audit_chain(
        batch_id=run_id,
        target_commit_sha=actual_commit,
        record_commit_sha=record.target_commit_sha,
        checks=checks,
    )

    digests = (
        sha256(
            json.dumps(
                asdict(record), sort_keys=True, default=str
            ).encode()
        ).hexdigest(),
        sha256(
            json.dumps(
                asdict(accepted), sort_keys=True, default=str
            ).encode()
        ).hexdigest(),
        reconciliation.snapshot_digest,
        sha256(
            json.dumps(
                asdict(audit), sort_keys=True, default=str
            ).encode()
        ).hexdigest(),
    )
    closure = create_closure(
        batch_id=run_id,
        target_commit_sha=actual_commit,
        chain_digests=digests,
    )
    closed = verify_closure(closure, digests)

    proof = plan_proof_run(
        run_id=run_id,
        target_commit_sha=actual_commit,
    )
    observations = tuple(
        f"{c.criterion_id}:{c.observed}" for c in criteria
    )
    proof = complete_proof_run(proof, observations, closed and record.passed)

    out = root / "proof-run-evidence.json"
    out.write_text(
        json.dumps(
            {
                "record": asdict(record),
                "acceptance": asdict(accepted),
                "reconciliation": asdict(reconciliation),
                "audit": asdict(audit),
                "closure": asdict(closure),
                "closure_verified": closed,
                "proof": asdict(proof),
            },
            sort_keys=True,
            indent=2,
            default=str,
        )
    )
    return 0 if closed and proof.state.value == "PASSED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
