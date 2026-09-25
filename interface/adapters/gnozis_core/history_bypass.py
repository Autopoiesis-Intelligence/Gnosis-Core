#!/usr/bin/env python3
"""Adversarial history-boundary probe for the existing Core."""
from __future__ import annotations
import argparse, hashlib, json, subprocess
from pathlib import Path
from gnosis.core.budget import Budget
from gnosis.core.evolution import Engine
from gnosis.core.types import Candidate, State

def sha(v):
    return hashlib.sha256(json.dumps(v, sort_keys=True, default=str, separators=(",",":")).encode()).hexdigest()

def rev():
    return subprocess.check_output(["git","rev-parse","HEAD"], text=True).strip()

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--core-revision",required=True); p.add_argument("--execution-id",required=True); p.add_argument("--report")
    a=p.parse_args(); actual=rev()
    if actual != a.core_revision:
        result="BLOCKED"; checks=[{"case":"target_revision_identity","result":"BLOCKED"}]
    else:
        engine=Engine(state=State(), budget=Budget(total=1))
        before=tuple(engine.history)
        try:
            engine.history.append("INTERFACE_DIRECT_MUTATION")
            after=tuple(engine.history)
            # This probe intentionally records the observed boundary. It does not
            # mutate or repair Core and therefore cannot label a mutable list safe.
            result="FAIL" if after != before else "PASS"
            checks=[{"case":"history-bypass","result":result,"before_length":len(before),"after_length":len(after),
                     "observation":"Engine.history accepts direct append" if after != before else "direct append rejected"}]
        except Exception as exc:
            result="PASS"
            checks=[{"case":"history-bypass","result":"PASS","observation":"direct append rejected","exception":type(exc).__name__}]
    evidence={"execution_id":a.execution_id,"contract_id":"CORE-MUTATION-BOUNDARY-01","contract_version":"1.0",
              "core_revision":actual,"declared_core_revision":a.core_revision,"checks":checks}
    record={**evidence,"result":result,"input_digest":sha({"execution_id":a.execution_id,"core_revision":a.core_revision}),
            "evidence_digest":sha(evidence)}
    out=json.dumps(record,indent=2,sort_keys=True)+"\n"
    if a.report: Path(a.report).write_text(out,encoding="utf-8")
    print(out,end="")
    return 0 if result=="PASS" else 1
if __name__=="__main__": raise SystemExit(main())
