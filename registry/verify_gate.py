#!/usr/bin/env python3
"""Independent fail-closed verification gate for evolution proposals."""
import hashlib, json
from dataclasses import dataclass

@dataclass(frozen=True)
class VerifyPolicy:
    policy_id: str
    policy_revision: str
    require_evidence: bool = True
    require_provenance: bool = True
    require_transition: bool = True


def digest(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()

def verify(result, previous_state, proposed_state, evidence, provenance, policy):
    errors=[]
    if result.get("result") != "PROPOSED": errors.append("result_not_proposed")
    if result.get("evolution_policy_id") != policy.policy_id or result.get("evolution_policy_revision") != policy.policy_revision: errors.append("policy_mismatch")
    if policy.require_transition and not result.get("proposed_transition"): errors.append("missing_transition")
    if policy.require_evidence and not evidence: errors.append("missing_evidence")
    if policy.require_provenance and not provenance: errors.append("missing_provenance")
    if not previous_state: errors.append("missing_previous_state")
    if not proposed_state: errors.append("missing_proposed_state")
    if proposed_state == previous_state: errors.append("no_state_change")
    if result.get("input_sha256") != digest({"candidate_id":result.get("candidate_id")}):
        # Input digest is checked against the externally supplied canonical reference;
        # this reference implementation requires an explicit verifier reference.
        errors.append("input_reference_not_reproducible")
    if evidence and any(not isinstance(x,str) or not x for x in evidence): errors.append("invalid_evidence_reference")
    if provenance and any(not isinstance(x,str) or not x for x in provenance): errors.append("invalid_provenance_reference")
    material={"verification_version":"0.1","candidate_id":result.get("candidate_id"),"evolution_id":result.get("evolution_id"),"policy_id":policy.policy_id,"policy_revision":policy.policy_revision,"previous_state_digest":digest(previous_state),"proposed_state_digest":digest(proposed_state),"evidence":evidence,"provenance":provenance,"status":"VERIFIED" if not errors else "REJECTED"}
    material["verification_sha256"]=digest(material)
    return {"result":"VERIFIED" if not errors else "REJECTED","errors":errors,"verification":material}

def main():
    import sys
    if len(sys.argv)!=2: print("usage: verify_gate.py verification.json"); return 2
    x=json.loads(open(sys.argv[1],encoding="utf-8").read()); p=VerifyPolicy(**x["policy"])
    out=verify(x["result"],x["previous_state"],x["proposed_state"],x.get("evidence",[]),x.get("provenance",[]),p)
    print(json.dumps(out,indent=2,ensure_ascii=False)); return 0 if out["result"]=="VERIFIED" else 1
if __name__=="__main__": raise SystemExit(main())
