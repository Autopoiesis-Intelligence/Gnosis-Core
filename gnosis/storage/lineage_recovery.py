"""Canonical lineage reconstruction independent of SQLite row order."""
from __future__ import annotations
import sqlite3
from dataclasses import dataclass

@dataclass(frozen=True)
class LineageStep:
    transition_id: str
    from_state_id: str
    to_state_id: str

def reconstruct_lineage(conn: sqlite3.Connection) -> tuple[LineageStep, ...]:
    rows=conn.execute("SELECT transition_id,from_state_id,to_state_id FROM evolution_transitions").fetchall()
    steps={r[0]:LineageStep(*r) for r in rows}
    if not steps: return ()
    children={}
    incoming={}
    for s in steps.values():
        children.setdefault(s.from_state_id,[]).append(s)
        incoming[s.to_state_id]=incoming.get(s.to_state_id,0)+1
    roots=[s for s in steps.values() if s.from_state_id not in incoming]
    if len(roots)!=1: raise ValueError("lineage must have exactly one root")
    ordered=[]; current=roots[0]; seen=set()
    while current:
        if current.transition_id in seen: raise ValueError("lineage cycle detected")
        seen.add(current.transition_id); ordered.append(current)
        nxt=children.get(current.to_state_id,[])
        if len(nxt)>1: raise ValueError("lineage branches are not canonical")
        current=nxt[0] if nxt else None
    if len(seen)!=len(steps): raise ValueError("disconnected lineage")
    return tuple(ordered)
