#!/usr/bin/env python3
"""Deterministic policy evaluation and authorization audit record."""
import hashlib
import json
from dataclasses import asdict, dataclass

@dataclass(frozen=True)
class Policy:
    policy_id: str
    policy_revision: str
    allowed_states: tuple
    domains: tuple
    operations: tuple
    resource_types: tuple
    update_modes: tuple

@dataclass(frozen=True)
class Request:
    request_id: str
    source_id: str
    lifecycle_state: str
    domain: str
    operation: str
    resource_type: str
    update_mode: str


def evaluate(policy: Policy, req: Request):
    reasons = []
    if req.lifecycle_state not in policy.allowed_states: reasons.append("lifecycle_state_denied")
    if req.domain not in policy.domains: reasons.append("domain_denied")
    if req.operation not in policy.operations: reasons.append("operation_denied")
    if req.resource_type not in policy.resource_types: reasons.append("resource_type_denied")
    if req.update_mode not in policy.update_modes: reasons.append("update_mode_denied")
    return reasons


def audit(policy, req, reasons):
    decision = "DENY" if reasons else "ALLOW"
    material = json.dumps({"policy":asdict(policy),"request":asdict(req),"decision":decision,"reasons":reasons}, sort_keys=True, separators=(",",":"))
    return {"audit_version":"0.1","request_id":req.request_id,"source_id":req.source_id,"policy_id":policy.policy_id,"policy_revision":policy.policy_revision,"decision":decision,"reasons":reasons,"decision_sha256":hashlib.sha256(material.encode()).hexdigest()}


def main():
    import sys
    if len(sys.argv) != 2:
        print("usage: policy_engine.py request.json"); return 2
    item = json.loads(open(sys.argv[1], encoding="utf-8").read())
    policy = Policy(**{k: tuple(v) if isinstance(v, list) else v for k,v in item["policy"].items()})
    req = Request(**item["request"])
    reasons = evaluate(policy, req)
    print(json.dumps(audit(policy, req, reasons), indent=2))
    return 1 if reasons else 0

if __name__ == "__main__": raise SystemExit(main())
