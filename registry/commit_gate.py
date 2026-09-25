#!/usr/bin/env python3
"""Fail-closed final gate; produces a commit authorization, never performs the commit."""
import hashlib,json
from dataclasses import dataclass

@dataclass(frozen=True)
class CommitPolicy:
    policy_id:str
    policy_revision:str
    require_verified:bool=True
    reject_noop:bool=True

def digest(x): return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()

def authorize(verification, previous_state, proposed_state, execution_input_sha256, policy, commit_id):
    errors=[]
    if verification.get("result") != "VERIFIED": errors.append("verification_not_verified")
    v=verification.get("verification",{})
    if v.get("policy_id") != policy.policy_id or v.get("policy_revision") != policy.policy_revision: errors.append("policy_mismatch")
    if not execution_input_sha256 or len(execution_input_sha256)!=64: errors.append("invalid_execution_input_digest")
    if previous_state == proposed_state: errors.append("no_op_transition")
    if v.get("previous_state_digest") != digest(previous_state): errors.append("previous_state_mismatch")
    if v.get("proposed_state_digest") != digest(proposed_state): errors.append("proposed_state_mismatch")
    if not commit_id: errors.append("missing_commit_id")
    material={"authorization_version":"0.1","commit_id":commit_id,"policy_id":policy.policy_id,"policy_revision":policy.policy_revision,"execution_input_sha256":execution_input_sha256,"previous_state_digest":digest(previous_state),"proposed_state_digest":digest(proposed_state),"verification_sha256":v.get("verification_sha256"),"status":"AUTHORIZED" if not errors else "REJECTED"}
    material["authorization_sha256"]=digest(material)
    return {"result":"AUTHORIZED" if not errors else "REJECTED","errors":errors,"authorization":material}

def main():
 import sys
 if len(sys.argv)!=2: print("usage: commit_gate.py commit.json"); return 2
 x=json.loads(open(sys.argv[1],encoding="utf-8").read()); p=CommitPolicy(**x["policy"])
 o=authorize(x["verification"],x["previous_state"],x["proposed_state"],x["execution_input_sha256"],p,x["commit_id"])
 print(json.dumps(o,indent=2,ensure_ascii=False)); return 0 if o["result"]=="AUTHORIZED" else 1
if __name__=="__main__": raise SystemExit(main())
