#!/usr/bin/env python3
"""Deterministic evolution-result contract; no commit authority."""
import hashlib, json
from dataclasses import dataclass

VALID = {"PROPOSED", "NO_CHANGE", "REJECTED", "FAILED"}

@dataclass(frozen=True)
class EvolutionResult:
    result_version: str
    candidate_id: str
    evolution_id: str
    evolution_policy_id: str
    evolution_policy_revision: str
    input_sha256: str
    result: str
    proposed_transition: object
    evidence: tuple
    counterexamples: tuple
    deterministic: bool
    result_sha256: str


def canonical(r):
    return json.dumps({"result_version":r.result_version,"candidate_id":r.candidate_id,"evolution_id":r.evolution_id,"evolution_policy_id":r.evolution_policy_id,"evolution_policy_revision":r.evolution_policy_revision,"input_sha256":r.input_sha256,"result":r.result,"proposed_transition":r.proposed_transition,"evidence":list(r.evidence),"counterexamples":list(r.counterexamples),"deterministic":r.deterministic},sort_keys=True,separators=(",",":"),ensure_ascii=False)

def validate(r):
    errors=[]
    if r.result_version != "0.1": errors.append("unsupported_result_version")
    if not r.candidate_id or not r.evolution_id: errors.append("missing_identity")
    if not r.evolution_policy_id or not r.evolution_policy_revision: errors.append("missing_policy")
    if len(r.input_sha256)!=64: errors.append("invalid_input_digest")
    if r.result not in VALID: errors.append("invalid_result")
    if not r.deterministic: errors.append("non_deterministic_result")
    if r.result == "PROPOSED" and not r.proposed_transition: errors.append("proposal_requires_transition")
    if r.result == "PROPOSED" and not r.evidence: errors.append("proposal_requires_evidence")
    if hashlib.sha256(canonical(r).encode()).hexdigest().lower()!=r.result_sha256.lower(): errors.append("result_digest_mismatch")
    return errors

def main():
    import sys
    if len(sys.argv)!=2: print("usage: evolution_result.py result.json"); return 2
    x=json.loads(open(sys.argv[1],encoding="utf-8").read()); r=EvolutionResult(**{k:tuple(v) if isinstance(v,list) else v for k,v in x.items()})
    errors=validate(r); print(json.dumps({"validator":"gnozis-evolution-result","version":"0.1","result":"PASS" if not errors else "FAIL","errors":errors},indent=2,ensure_ascii=False)); return 1 if errors else 0
if __name__=="__main__": raise SystemExit(main())
