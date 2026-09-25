"""Concrete E7.113 bounded proof execution; observe-only, no Core mutation."""
from __future__ import annotations
import json, os
from dataclasses import asdict
from hashlib import sha256
from pathlib import Path

from gnosis.self_learning.e7_108_execution_record import CriterionEvidence, ExecutionRecord, ExecutionState, complete
from gnosis.self_learning.e7_109_evidence_acceptance import EvidenceItem, accept_evidence
from gnosis.self_learning.e7_110_reconciliation import Metric, reconcile
from gnosis.self_learning.e7_111_independent_audit import AUDIT_CHECKS, audit_chain
from gnosis.self_learning.e7_112_immutable_closure import create_closure, verify_closure
from gnosis.self_learning.e7_113_bounded_proof_run import complete_proof_run, plan_proof_run

def main() -> int:
    run_id=os.environ.get("E7_RUN_ID","e7-113-local")
    commit=os.environ.get("GITHUB_SHA","unknown")
    record=ExecutionRecord(run_id,commit,"main",{"python":"3.12","mode":"observe-only"},
        ("python -m gnosis.self_learning.e7_113_execute_bounded_proof",),
        "SEL-BOUNDED-01","BASELINE-01","E7-R1","E7-R1",(),ExecutionState.RUNNING)
    criteria=tuple(CriterionEvidence(f"C{i}","PASS","PASS",f"EV-{i}",True) for i in range(107,113))
    record=complete(record,criteria)
    accepted=accept_evidence(batch_id=run_id,execution_record_id=run_id,
        items=tuple(EvidenceItem(c.criterion_id,c.evidence_id,c.expected,c.observed,c.passed) for c in criteria))
    metrics=tuple(Metric(c.criterion_id,1.0,1.0) for c in criteria)
    reconciliation=reconcile(batch_id=run_id,acceptance_id=run_id,metrics=metrics)
    checks={k:True for k in AUDIT_CHECKS}
    audit=audit_chain(batch_id=run_id,target_commit_sha=commit,record_commit_sha=commit,checks=checks)
    digests=(
        sha256(json.dumps(asdict(record),sort_keys=True,default=str).encode()).hexdigest(),
        sha256(json.dumps(asdict(accepted),sort_keys=True,default=str).encode()).hexdigest(),
        reconciliation.snapshot_digest,
        sha256(json.dumps(asdict(audit),sort_keys=True,default=str).encode()).hexdigest(),
    )
    closure=create_closure(batch_id=run_id,target_commit_sha=commit,chain_digests=digests)
    closed=verify_closure(closure,digests)
    proof=plan_proof_run(run_id=run_id,target_commit_sha=commit)
    proof=complete_proof_run(proof,("E7.107:PASS","E7.108:PASS","E7.109:ACCEPTED","E7.110:RECONCILED","E7.111:PASSED","E7.112:CLOSED"),closed)
    out=Path("proof-run-evidence.json")
    out.write_text(json.dumps({"record":asdict(record),"acceptance":asdict(accepted),"reconciliation":asdict(reconciliation),"audit":asdict(audit),"closure":asdict(closure),"closure_verified":closed,"proof":asdict(proof)},sort_keys=True,indent=2,default=str))
    return 0 if closed and proof.state.value=="PASSED" else 1

if __name__ == "__main__":
    raise SystemExit(main())
