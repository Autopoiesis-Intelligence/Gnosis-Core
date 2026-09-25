#!/usr/bin/env python3
"""Non-authoritative handoff from Federation authorization to the existing Core bridge."""
import hashlib,json
from dataclasses import dataclass

@dataclass(frozen=True)
class FederationCoreHandoff:
    version:str
    federation_authorization_sha256:str
    candidate_id:str
    source_id:str
    resource_id:str
    target:str
    action:str
    evidence_refs:tuple
    status:str
    handoff_sha256:str

def digest(x):
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()

def create_handoff(authorization,candidate,target,action,evidence_refs):
    errors=[]
    if authorization.get("result") != "AUTHORIZED": errors.append("federation_not_authorized")
    if not candidate.get("candidate_id"): errors.append("missing_candidate_id")
    if not candidate.get("source_id") or not candidate.get("resource_id"): errors.append("missing_source_identity")
    if not target or not action: errors.append("missing_target_or_action")
    if not evidence_refs: errors.append("missing_evidence_refs")
    if errors: return {"result":"REJECT","errors":errors}
    item={"version":"0.1","federation_authorization_sha256":authorization.get("authorization_sha256",""),"candidate_id":candidate["candidate_id"],"source_id":candidate["source_id"],"resource_id":candidate["resource_id"],"target":target,"action":action,"evidence_refs":list(evidence_refs),"status":"PENDING_CORE_AUTHORITY"}
    item["handoff_sha256"]=digest(item)
    return {"result":"HANDOFF_READY","handoff":item}

def main():
 import sys
 if len(sys.argv)!=2: print("usage: core_handoff.py handoff.json"); return 2
 x=json.loads(open(sys.argv[1],encoding="utf-8").read())
 print(json.dumps(create_handoff(x["authorization"],x["candidate"],x["target"],x["action"],x["evidence_refs"]),indent=2,ensure_ascii=False)); return 0
if __name__=="__main__": raise SystemExit(main())
