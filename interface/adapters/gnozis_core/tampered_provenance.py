#!/usr/bin/env python3
"""Execute the existing recovery test as contract evidence."""
from __future__ import annotations
import argparse, json, subprocess, hashlib
from pathlib import Path

def sha(v):
    return hashlib.sha256(json.dumps(v,sort_keys=True,default=str,separators=(",",":")).encode()).hexdigest()

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--core-revision",required=True); p.add_argument("--execution-id",required=True); p.add_argument("--report")
    a=p.parse_args()
    actual=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()
    if actual != a.core_revision:
        result="BLOCKED"; checks=[{"case":"target_revision_identity","result":"BLOCKED"}]
    else:
        cmd=["python","-m","pytest","-q","tests/test_evolution_recovery.py","-k","tampered"]
        run=subprocess.run(cmd,text=True,capture_output=True)
        result="PASS" if run.returncode==0 else "FAIL"
        checks=[{"case":"tampered-provenance-recovery","result":result,
                 "command":" ".join(cmd),"returncode":run.returncode,
                 "stdout":run.stdout[-4000:],"stderr":run.stderr[-4000:]}]
    evidence={"execution_id":a.execution_id,"contract_id":"CORE-MUTATION-BOUNDARY-01","contract_version":"1.0",
              "case":"tampered-provenance","core_revision":actual,"declared_core_revision":a.core_revision,"checks":checks}
    record={**evidence,"result":result,"input_digest":sha({"execution_id":a.execution_id,"core_revision":a.core_revision}),
            "evidence_digest":sha(evidence)}
    out=json.dumps(record,indent=2,sort_keys=True)+"\n"
    if a.report: Path(a.report).write_text(out,encoding="utf-8")
    print(out,end="")
    return 0 if result=="PASS" else 1
if __name__=="__main__": raise SystemExit(main())
