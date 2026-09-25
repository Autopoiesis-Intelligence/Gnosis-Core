#!/usr/bin/env python3
"""Deterministic selection over validated test results; no source authority."""
import hashlib
import json
from dataclasses import dataclass

@dataclass(frozen=True)
class SelectionPolicy:
    policy_id: str
    policy_revision: str
    admissible_results: tuple
    require_evidence: bool = True


def canonical(item):
    return json.dumps(item, sort_keys=True, separators=(",",":"), ensure_ascii=False)


def select(results, policy):
    errors=[]
    admissible=[]
    for r in results:
        if r.get("result") not in policy.admissible_results: continue
        if policy.require_evidence and not r.get("evidence"): continue
        if not r.get("candidate_id") or not r.get("result_sha256"): continue
        admissible.append(r)
    if not admissible:
        return {"result":"NO_SELECTION","policy_id":policy.policy_id,"policy_revision":policy.policy_revision,"errors":["no_admissible_result"]}
    # Stable ordering is the only selector authority: evidence-backed PASS first,
    # then deterministic lexical candidate identity. Source identity is ignored.
    admissible.sort(key=lambda r:(r.get("result") != "PASS", r["candidate_id"]))
    chosen=admissible[0]
    selected={"selection_version":"0.1","candidate_id":chosen["candidate_id"],"test_result_sha256":chosen["result_sha256"],"policy_id":policy.policy_id,"policy_revision":policy.policy_revision,"selection_rule":"PASS_THEN_CANDIDATE_ID","status":"selected_for_evolution"}
    selected["selection_sha256"]=hashlib.sha256(canonical(selected).encode()).hexdigest()
    return {"result":"SELECTED","selection":selected}


def main():
    import sys
    if len(sys.argv)!=2: print("usage: select_isolation.py selection.json"); return 2
    item=json.loads(open(sys.argv[1],encoding="utf-8").read())
    p=SelectionPolicy(**{k:tuple(v) if isinstance(v,list) else v for k,v in item["policy"].items()})
    print(json.dumps(select(item["results"],p),indent=2,ensure_ascii=False)); return 0

if __name__=="__main__": raise SystemExit(main())
