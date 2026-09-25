#!/usr/bin/env python3
"""Deterministic, capability-free test result contract."""
import hashlib
import json
from dataclasses import dataclass

VALID_RESULTS = {"PASS", "FAIL", "INCONCLUSIVE", "REJECTED"}

@dataclass(frozen=True)
class TestResult:
    result_version: str
    candidate_id: str
    test_id: str
    test_policy_id: str
    test_policy_revision: str
    input_digest: str
    result: str
    evidence: tuple
    counterexamples: tuple
    deterministic: bool
    result_sha256: str


def canonical(r):
    return json.dumps({"result_version":r.result_version,"candidate_id":r.candidate_id,"test_id":r.test_id,"test_policy_id":r.test_policy_id,"test_policy_revision":r.test_policy_revision,"input_digest":r.input_digest,"result":r.result,"evidence":list(r.evidence),"counterexamples":list(r.counterexamples),"deterministic":r.deterministic}, sort_keys=True, separators=(",",":"), ensure_ascii=False)


def validate(r):
    errors=[]
    if r.result_version != "0.1": errors.append("unsupported_result_version")
    if not r.candidate_id or not r.test_id: errors.append("missing_identity")
    if not r.test_policy_id or not r.test_policy_revision: errors.append("missing_test_policy")
    if len(r.input_digest)!=64: errors.append("invalid_input_digest")
    if r.result not in VALID_RESULTS: errors.append("invalid_result")
    if not r.deterministic: errors.append("non_deterministic_result")
    if hashlib.sha256(canonical(r).encode()).hexdigest().lower()!=r.result_sha256.lower(): errors.append("result_digest_mismatch")
    if r.result == "PASS" and not r.evidence: errors.append("pass_requires_evidence")
    if r.result == "FAIL" and not r.counterexamples: errors.append("fail_requires_counterexample")
    return errors


def main():
    import sys
    if len(sys.argv)!=2: print("usage: test_result.py result.json"); return 2
    r=TestResult(**{k:tuple(v) if isinstance(v,list) else v for k,v in json.loads(open(sys.argv[1],encoding="utf-8").read()).items()})
    errors=validate(r)
    print(json.dumps({"validator":"gnozis-test-result","version":"0.1","result":"PASS" if not errors else "FAIL","errors":errors},indent=2,ensure_ascii=False)); return 1 if errors else 0

if __name__=="__main__": raise SystemExit(main())
