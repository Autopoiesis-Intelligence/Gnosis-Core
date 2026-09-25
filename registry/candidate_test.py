#!/usr/bin/env python3
"""Deterministic isolated test admission for federated candidates."""
import hashlib
import json
from dataclasses import dataclass

@dataclass(frozen=True)
class Candidate:
    candidate_version: str
    candidate_id: str
    source_id: str
    resource_id: str
    domain: str
    resource_type: str
    policy_id: str
    policy_revision: str
    evidence_ref: str
    status: str
    candidate_sha256: str

@dataclass(frozen=True)
class TestPolicy:
    policy_id: str
    policy_revision: str
    allowed_domains: tuple
    allowed_resource_types: tuple


def canonical(c):
    return json.dumps({"candidate_version":c.candidate_version,"candidate_id":c.candidate_id,"source_id":c.source_id,"resource_id":c.resource_id,"domain":c.domain,"resource_type":c.resource_type,"policy_id":c.policy_id,"policy_revision":c.policy_revision,"evidence_ref":c.evidence_ref,"status":c.status}, sort_keys=True, separators=(",",":"), ensure_ascii=False)


def admit_for_test(c, p):
    errors=[]
    if c.status != "candidate_pending_test": errors.append("candidate_not_pending_test")
    if c.policy_id != p.policy_id: errors.append("policy_id_mismatch")
    if c.policy_revision != p.policy_revision: errors.append("policy_revision_mismatch")
    if c.domain not in p.allowed_domains: errors.append("domain_not_allowed")
    if c.resource_type not in p.allowed_resource_types: errors.append("resource_type_not_allowed")
    if hashlib.sha256(canonical(c).encode()).hexdigest().lower() != c.candidate_sha256.lower(): errors.append("candidate_digest_mismatch")
    if not c.evidence_ref: errors.append("missing_evidence_ref")
    if errors: return {"result":"REJECT","errors":errors}
    test_input={"test_input_version":"0.1","candidate_id":c.candidate_id,"evidence_ref":c.evidence_ref,"test_policy_id":p.policy_id,"test_policy_revision":p.policy_revision,"execution_capabilities":[],"mutation_capabilities":[],"selector_capabilities":[]}
    test_input["test_input_sha256"]=hashlib.sha256(json.dumps(test_input, sort_keys=True, separators=(",",":"), ensure_ascii=False).encode()).hexdigest()
    return {"result":"ADMITTED_FOR_ISOLATED_TEST","test_input":test_input}


def main():
    import sys
    if len(sys.argv)!=2: print("usage: candidate_test.py test.json"); return 2
    item=json.loads(open(sys.argv[1],encoding="utf-8").read())
    c=Candidate(**item["candidate"]); p=TestPolicy(**{k:tuple(v) if isinstance(v,list) else v for k,v in item["policy"].items()})
    print(json.dumps(admit_for_test(c,p),indent=2,ensure_ascii=False)); return 0

if __name__=="__main__": raise SystemExit(main())
