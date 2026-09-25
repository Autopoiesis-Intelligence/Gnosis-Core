#!/usr/bin/env python3
"""Adversarial alternate-authority probe for deterministic Select."""
from __future__ import annotations
import argparse, hashlib, json, subprocess
from pathlib import Path
from gnosis.core.budget import Budget
from gnosis.core.evolution import Engine
from gnosis.core.types import Candidate, State

def digest(v):
    return hashlib.sha256(json.dumps(v,sort_keys=True,default=str,separators=(",",":")).encode()).hexdigest()

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--core-revision",required=True); p.add_argument("--execution-id",required=True); p.add_argument("--report")
    a=p.parse_args(); actual=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()
    checks=[]
    if actual != a.core_revision:
        result="BLOCKED"; checks.append({"case":"target_revision_identity","result":"BLOCKED"})
    else:
        state=State()
        # Deliberately adversarial: candidates are supplied in reverse order.
        # Canonical Select must still choose the smallest passing candidate_id.
        candidates=[
            Candidate(parent_state_id=state.state_id,proposed_state=State(elements={"z":1}),origin="z-authority"),
            Candidate(parent_state_id=state.state_id,proposed_state=State(elements={"a":1}),origin="a-authority"),
        ]
        engine=Engine(state=state,budget=Budget(total=1))
        record=engine.step_select(candidates)
        result="PASS" if record.candidate_id==candidates[1].candidate_id else "FAIL"
        checks.append({"case":"alternate-authority","result":result,
                       "selected_candidate_id":record.candidate_id,
                       "expected_candidate_origin":"a-authority",
                       "selection_order":["z-authority","a-authority"],
                       "observation":"selection remains deterministic despite adversarial input order"})
    evidence={"execution_id":a.execution_id,"contract_id":"CORE-MUTATION-BOUNDARY-01","contract_version":"1.0",
              "case":"alternate-authority","core_revision":actual,"declared_core_revision":a.core_revision,"checks":checks}
    record={**evidence,"result":result,"input_digest":digest({"execution_id":a.execution_id,"core_revision":a.core_revision}),
            "evidence_digest":digest(evidence)}
    out=json.dumps(record,indent=2,sort_keys=True)+"\n"
    if a.report: Path(a.report).write_text(out,encoding="utf-8")
    print(out,end="")
    return 0 if result=="PASS" else 1
if __name__=="__main__": raise SystemExit(main())
