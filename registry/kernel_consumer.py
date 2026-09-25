#!/usr/bin/env python3
"""Fail-closed Kernel-side consumer for federated information envelopes."""
import hashlib
import json
from dataclasses import dataclass

@dataclass(frozen=True)
class Envelope:
    envelope_version: str
    request_id: str
    source_id: str
    resource_id: str
    domain: str
    resource_type: str
    policy_revision: str
    content_sha256: str
    payload: object
    mutation_allowed: bool
    execution_allowed: bool
    envelope_sha256: str


def canonical_without_digest(e: Envelope):
    data = {
        "envelope_version": e.envelope_version, "request_id": e.request_id,
        "source_id": e.source_id, "resource_id": e.resource_id,
        "domain": e.domain, "resource_type": e.resource_type,
        "policy_revision": e.policy_revision, "content_sha256": e.content_sha256,
        "payload": e.payload, "mutation_allowed": e.mutation_allowed,
        "execution_allowed": e.execution_allowed,
    }
    return json.dumps(data, sort_keys=True, separators=(",",":"), ensure_ascii=False)


def consume(e: Envelope):
    errors = []
    if e.envelope_version != "0.1": errors.append("unsupported_envelope_version")
    for key in ("request_id", "source_id", "resource_id", "policy_revision", "content_sha256", "envelope_sha256"):
        if not getattr(e, key): errors.append(f"missing_{key}")
    if len(e.content_sha256) != 64 or any(c not in "0123456789abcdefABCDEF" for c in e.content_sha256): errors.append("invalid_content_sha256")
    expected = hashlib.sha256(canonical_without_digest(e).encode()).hexdigest()
    if expected.lower() != e.envelope_sha256.lower(): errors.append("envelope_digest_mismatch")
    if e.mutation_allowed: errors.append("mutation_capability_forbidden")
    if e.execution_allowed: errors.append("execution_capability_forbidden")
    if errors: return {"result":"REJECT","errors":errors}
    observation = {
        "observation_version":"0.1",
        "source_id":e.source_id,
        "resource_id":e.resource_id,
        "domain":e.domain,
        "resource_type":e.resource_type,
        "policy_revision":e.policy_revision,
        "content_sha256":e.content_sha256,
        "payload":e.payload,
        "influence_status":"not_authorized",
    }
    observation["observation_sha256"] = hashlib.sha256(json.dumps(observation, sort_keys=True, separators=(",",":"), ensure_ascii=False).encode()).hexdigest()
    return {"result":"ACCEPT_AS_OBSERVATION","observation":observation}


def main():
    import sys
    if len(sys.argv) != 2:
        print("usage: kernel_consumer.py envelope.json"); return 2
    e = Envelope(**json.loads(open(sys.argv[1], encoding="utf-8").read()))
    print(json.dumps(consume(e), indent=2, ensure_ascii=False))
    return 0

if __name__ == "__main__": raise SystemExit(main())
