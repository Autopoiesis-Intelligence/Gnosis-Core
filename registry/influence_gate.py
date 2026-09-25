#!/usr/bin/env python3
"""Fail-closed gate between external observations and Core candidate admission."""
import hashlib
import json
from dataclasses import dataclass

@dataclass(frozen=True)
class Observation:
    observation_version: str
    source_id: str
    resource_id: str
    domain: str
    resource_type: str
    policy_revision: str
    content_sha256: str
    payload: object
    influence_status: str
    observation_sha256: str

@dataclass(frozen=True)
class AdmissionPolicy:
    policy_id: str
    policy_revision: str
    allowed_domains: tuple
    allowed_resource_types: tuple
    minimum_status: str = "not_authorized"


def canonical(o: Observation):
    return json.dumps({
        "observation_version":o.observation_version,"source_id":o.source_id,
        "resource_id":o.resource_id,"domain":o.domain,"resource_type":o.resource_type,
        "policy_revision":o.policy_revision,"content_sha256":o.content_sha256,
        "payload":o.payload,"influence_status":o.influence_status,
    }, sort_keys=True, separators=(",",":"), ensure_ascii=False)


def admit(o: Observation, p: AdmissionPolicy):
    errors = []
    if o.observation_version != "0.1": errors.append("unsupported_observation_version")
    if o.influence_status != "not_authorized": errors.append("invalid_external_influence_status")
    if o.domain not in p.allowed_domains: errors.append("domain_not_admissible")
    if o.resource_type not in p.allowed_resource_types: errors.append("resource_type_not_admissible")
    if not o.source_id or not o.resource_id: errors.append("missing_identity")
    if len(o.content_sha256) != 64: errors.append("invalid_content_digest")
    expected = hashlib.sha256(canonical(o).encode()).hexdigest()
    if expected.lower() != o.observation_sha256.lower(): errors.append("observation_digest_mismatch")
    if errors: return {"result":"REJECT","errors":errors}
    material = {"candidate_version":"0.1","candidate_id":o.observation_sha256[:24],"source_id":o.source_id,"resource_id":o.resource_id,"domain":o.domain,"resource_type":o.resource_type,"policy_id":p.policy_id,"policy_revision":p.policy_revision,"evidence_ref":o.observation_sha256,"status":"candidate_pending_test"}
    material["candidate_sha256"] = hashlib.sha256(json.dumps(material, sort_keys=True, separators=(",",":"), ensure_ascii=False).encode()).hexdigest()
    return {"result":"ADMITTED_AS_CANDIDATE","candidate":material}


def main():
    import sys
    if len(sys.argv) != 2:
        print("usage: influence_gate.py admission.json"); return 2
    item=json.loads(open(sys.argv[1], encoding="utf-8").read())
    o=Observation(**item["observation"]); p=AdmissionPolicy(**{k:tuple(v) if isinstance(v,list) else v for k,v in item["policy"].items()})
    print(json.dumps(admit(o,p), indent=2, ensure_ascii=False)); return 0

if __name__ == "__main__": raise SystemExit(main())
