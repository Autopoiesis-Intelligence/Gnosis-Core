#!/usr/bin/env python3
"""Deterministic registry lifecycle transition checker."""
import json
from dataclasses import dataclass

STATES = {"discovered", "registered", "authorized", "verified", "active", "quarantined", "revoked"}
TRANSITIONS = {
    "discovered": {"registered", "quarantined"},
    "registered": {"authorized", "quarantined"},
    "authorized": {"verified", "quarantined", "revoked"},
    "verified": {"active", "quarantined", "revoked"},
    "active": {"quarantined", "revoked"},
    "quarantined": {"verified", "revoked"},
    "revoked": set(),
}

@dataclass(frozen=True)
class Transition:
    source_id: str
    from_state: str
    to_state: str
    policy_revision: str
    actor: str
    reason: str


def validate(t: Transition):
    errors = []
    if not t.source_id: errors.append("missing_source_id")
    if t.from_state not in STATES: errors.append("invalid_from_state")
    if t.to_state not in STATES: errors.append("invalid_to_state")
    if t.to_state not in TRANSITIONS.get(t.from_state, set()): errors.append("illegal_transition")
    if not t.policy_revision: errors.append("missing_policy_revision")
    if not t.actor: errors.append("missing_actor")
    if not t.reason: errors.append("missing_reason")
    return errors


def main():
    import sys
    if len(sys.argv) != 2:
        print("usage: state_machine.py transition.json")
        return 2
    item = json.loads(open(sys.argv[1], encoding="utf-8").read())
    errors = validate(Transition(**item))
    print(json.dumps({"validator":"gnozis-registry-state-machine","version":"0.1","result":"FAIL" if errors else "PASS","errors":errors}, indent=2))
    return 1 if errors else 0

if __name__ == "__main__":
    raise SystemExit(main())
