"""Canonical reconstruction and verification of persisted transitions."""
from __future__ import annotations
import json, sqlite3
from gnosis.core.types import TransitionRecord, TestResult
from gnosis.core.transition_identity import transition_id

def load_transition(conn: sqlite3.Connection, stored_transition_id: str) -> TransitionRecord:
    row=conn.execute(
        "SELECT transition_id,candidate_id,from_state_id,to_state_id,payload "
        "FROM evolution_transitions WHERE transition_id=?",(stored_transition_id,)
    ).fetchone()
    if row is None:
        raise KeyError(stored_transition_id)
    payload=json.loads(row[4])
    columns={"from_state_id":row[2],"to_state_id":row[3],"candidate_id":row[1]}
    for name in columns:
        if payload.get(name) != columns[name]:
            raise ValueError("persisted transition payload identity mismatch")
    record=TransitionRecord(
        from_state_id=payload["from_state_id"], to_state_id=payload["to_state_id"], candidate_id=payload["candidate_id"],
        test_result=TestResult(bool(payload["test_passed"]), tuple(payload.get("test_reasons",()))),
        accepted=bool(payload["accepted"]), reason=payload["reason"],
        test_rule_id=payload.get("test_rule_id"),
    )
    computed=transition_id(record)
    if computed != row[0]:
        raise ValueError("persisted transition identity mismatch")
    return record
