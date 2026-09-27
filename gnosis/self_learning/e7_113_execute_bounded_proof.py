"""Concrete E7.113 bounded proof execution; observe-only, no Core mutation."""
from __future__ import annotations
import json, os, shlex, subprocess
from dataclasses import asdict
from hashlib import sha256
from pathlib import Path

from gnosis.self_learning.e7_108_execution_record import CriterionEvidence, ExecutionRecord, ExecutionState, complete
from gnosis.self_learning.e7_109_evidence_acceptance import EvidenceItem, accept_evidence
from gnosis.self_learning.e7_110_reconciliation import Metric, reconcile
from gnosis.self_learning.e7_111_independent_audit import AUDIT_CHECKS, audit_chain
from gnosis.self_learning.e7_112_immutable_closure import create_closure, verify_closure
from gnosis.self_learning.e7_113_bounded_proof_run import complete_proof_run, plan_proof_run
from gnosis.self_learning.e7_106_selection import SelectionRecord
from gnosis.self_learning.e7_114_preflight import assert_preflight_ready, run_preflight
from gnosis.self_learning.e7_114_scope_lock import ScopeLock

def execute_locked_command(*, scope_lock: ScopeLock, selection_record: SelectionRecord, repository_root: str | os.PathLike[str], resolved_commit_sha: str, resolved_branch_ref: str) -> tuple[int, str, str]:
    root = Path(repository_root)
    report = run_preflight(scope_lock, repository_root=root, resolved_commit_sha=resolved_commit_sha, resolved_branch_ref=resolved_branch_ref, selection_record=selection_record)
    assert_preflight_ready(report)
    if len(scope_lock.commands) != 1:
        raise ValueError("bounded proof execution requires exactly one locked command")
    argv = shlex.split(scope_lock.commands[0])
    if not argv:
        raise ValueError("locked execution command is empty")
    completed = subprocess.run(argv, cwd=root, capture_output=True, text=True, check=False)
    return completed.returncode, completed.stdout, completed.stderr

def main() -> int:
    raise SystemExit("E7.113 execution is fail-closed: frozen SelectionRecord + ScopeLock must be supplied to execute_locked_command")

if __name__ == "__main__":
    raise SystemExit(main())
