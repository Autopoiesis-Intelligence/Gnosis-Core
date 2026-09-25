#!/usr/bin/env python3
"""Fail-closed adapter that converts an authorized source into scoped input."""
import hashlib
import json
from dataclasses import dataclass

@dataclass(frozen=True)
class Authorization:
    source_id: str
    lifecycle_state: str
    domain: str
    operation: str
    resource_type: str
    update_mode: str
    policy_revision: str
    decision: str

@dataclass(frozen=True)
class ConsumptionRequest:
    request_id: str
    resource_id: str
    content_digest: str
    payload: object


def consume(auth: Authorization, req: ConsumptionRequest):
    errors = []
    if auth.decision != "ALLOW": errors.append("authorization_denied")
    if auth.lifecycle_state not in {"authorized", "verified", "active"}: errors.append("source_not_active_for_consumption")
    if auth.operation != "read": errors.append("consumption_requires_read_operation")
    if not auth.policy_revision: errors.append("missing_policy_revision")
    if not req.resource_id: errors.append("missing_resource_id")
    if len(req.content_digest) != 64: errors.append("invalid_content_digest")
    if errors: return {"result":"DENY","errors":errors}
    envelope = {
        "envelope_version":"0.1",
        "request_id":req.request_id,
        "source_id":auth.source_id,
        "resource_id":req.resource_id,
        "domain":auth.domain,
        "resource_type":auth.resource_type,
        "source_revision":auth.policy_revision,
        "content_sha256":req.content_digest,
        "payload":req.payload,
        "mutation_allowed":False,
        "execution_allowed":False,
    }
    canonical = json.dumps(envelope, sort_keys=True, separators=(",",":"), ensure_ascii=False)
    envelope["envelope_sha256"] = hashlib.sha256(canonical.encode()).hexdigest()
    return {"result":"ALLOW","envelope":envelope}


def main():
    import sys
    if len(sys.argv) != 2:
        print("usage: scoped_consumption.py request.json"); return 2
    item = json.loads(open(sys.argv[1], encoding="utf-8").read())
    auth = Authorization(**item["authorization"])
    req = ConsumptionRequest(**item["request"])
    print(json.dumps(consume(auth, req), indent=2, ensure_ascii=False))
    return 0

if __name__ == "__main__": raise SystemExit(main())
