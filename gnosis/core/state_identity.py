"""Canonical State digest for recovery verification."""
from __future__ import annotations
from gnosis.core.types import State, Relation, _stable_hash

def canonical_state_payload(state: State) -> dict:
    return {
        "elements": state.elements,
        "relations": [
            {"source": r.source, "target": r.target, "relation_type": r.relation_type, "value": r.value}
            for r in state.relations
        ],
        "version": state.version,
    }

def state_digest(state: State) -> str:
    return _stable_hash(canonical_state_payload(state))

def verify_state_digest(state: State, expected: str) -> bool:
    return bool(expected) and state_digest(state) == expected

def state_from_payload(payload: dict) -> State:
    relations=tuple(Relation(r["source"],r["target"],r["relation_type"],r.get("value")) for r in payload.get("relations",()))
    return State(elements=payload.get("elements",{}),relations=relations,version=int(payload.get("version",0)))
