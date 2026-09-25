#!/usr/bin/env python3
"""Deterministic authorization-scope evaluator for Memory Sources."""
import json
from dataclasses import dataclass

@dataclass(frozen=True)
class AuthorizationRequest:
    source_id: str
    lifecycle_state: str
    domain: str
    operation: str
    resource_type: str
    update_mode: str
    policy_revision: str

@dataclass(frozen=True)
class AuthorizationScope:
    domains: tuple
    operations: tuple
    resource_types: tuple
    update_modes: tuple


def evaluate(req: AuthorizationRequest, scope: AuthorizationScope):
    errors = []
    if req.lifecycle_state not in {"authorized", "verified", "active"}:
        errors.append("source_not_authorized")
    if req.domain not in scope.domains:
        errors.append("domain_not_in_scope")
    if req.operation not in scope.operations:
        errors.append("operation_not_in_scope")
    if req.resource_type not in scope.resource_types:
        errors.append("resource_type_not_in_scope")
    if req.update_mode not in scope.update_modes:
        errors.append("update_mode_not_in_scope")
    if not req.policy_revision:
        errors.append("missing_policy_revision")
    return errors


def main():
    import sys
    if len(sys.argv) != 2:
        print("usage: authorization.py request.json")
        return 2
    item = json.loads(open(sys.argv[1], encoding="utf-8").read())
    req = AuthorizationRequest(**item["request"])
    scope = AuthorizationScope(**{k: tuple(v) for k, v in item["scope"].items()})
    errors = evaluate(req, scope)
    print(json.dumps({"engine":"gnozis-authorization-scope","version":"0.1","result":"DENY" if errors else "ALLOW","errors":errors}, indent=2))
    return 1 if errors else 0

if __name__ == "__main__":
    raise SystemExit(main())
