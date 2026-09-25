#!/usr/bin/env python3
"""Fail-closed boundary from Select to the Evolution stage."""
import hashlib, json
from dataclasses import dataclass

@dataclass(frozen=True)
class Selection:
    selection_version: str
    candidate_id: str
    test_result_sha256: str
    policy_id: str
    policy_revision: str
    selection_rule: str
    status: str
    selection_sha256: str

@dataclass(frozen=True)
class EvolutionPolicy:
    policy_id: str
    policy_revision: str
    allowed_selection_status: tuple
    allowed_domains: tuple


def canonical(s):
    return json.dumps({k:getattr(s,k) for k in s.__dataclass_fields__ if k != "selection_sha256"},sort_keys=True,separators=(",",":"),ensure_ascii=False)

def prepare(s, p, domain):
    errors=[]
    if s.status not in p.allowed_selection_status: errors.append("selection_not_admissible")
    if s.policy_id != p.policy_id or s.policy_revision != p.policy_revision: errors.append("policy_mismatch")
    if domain not in p.allowed_domains: errors.append("domain_not_allowed")
    if hashlib.sha256(canonical(s).encode()).hexdigest().lower() != s.selection_sha256.lower(): errors.append("selection_digest_mismatch")
    if errors: return {"result":"REJECT","errors":errors}
    item={"evolution_input_version":"0.1","candidate_id":s.candidate_id,"test_result_sha256":s.test_result_sha256,"selection_sha256":s.selection_sha256,"policy_id":p.policy_id,"policy_revision":p.policy_revision,"domain":domain,"mutation_capabilities":[],"execution_capabilities":[],"commit_capabilities":[],"status":"pending_evolution"}
    item["evolution_input_sha256"]=hashlib.sha256(json.dumps(item,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
    return {"result":"ADMITTED_FOR_EVOLUTION","evolution_input":item}

def main():
    import sys
    if len(sys.argv)!=2: print("usage: evolution_input.py input.json"); return 2
    x=json.loads(open(sys.argv[1],encoding="utf-8").read()); s=Selection(**x["selection"]); p=EvolutionPolicy(**{k:tuple(v) if isinstance(v,list) else v for k,v in x["policy"].items()})
    print(json.dumps(prepare(s,p,x["domain"]),indent=2,ensure_ascii=False)); return 0
if __name__=="__main__": raise SystemExit(main())
