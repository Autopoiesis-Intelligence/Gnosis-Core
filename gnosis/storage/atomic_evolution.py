"""Atomic persistence of the complete evolution evidence graph."""
from __future__ import annotations
import json, sqlite3
from typing import Any, Mapping
from gnosis.evidence.audit import make_audit_record, EvolutionAuditRecord, verify_audit_chain
from gnosis.evidence.provenance import EvidenceProvenance, canonical_digest
from gnosis.core.durable_commit import DurableCommitResult
from gnosis.core.persistable_transition import PersistableTransition
from gnosis.core.types import TransitionRecord
from gnosis.core.transition_identity import transition_id as canonical_transition_id

def persist_evolution_with_evidence(conn: sqlite3.Connection, provenance: EvidenceProvenance, *,
    transition: TransitionRecord | None = None, transition_id: str | None = None, event_type: str, payload: Mapping[str, Any],
    observations: Mapping[str, Any], failure_after: str | None = None) -> DurableCommitResult:
    if canonical_digest(observations) != provenance.evidence_digest:
        raise ValueError("evidence digest does not match observations")
    if transition.candidate_id != provenance.candidate_id:
        raise ValueError("transition candidate does not match provenance")
    if transition is None:
        raise ValueError("transition is required")
    persistable=PersistableTransition(transition)
    derived_transition_id=persistable.transition_id
    if transition_id is not None and transition_id != derived_transition_id:
        raise ValueError("transition identity mismatch")
    transition_id=derived_transition_id
    if not canonical_transition_id(transition) == transition_id:
        raise ValueError("transition identity derivation failed")
    owns=not conn.in_transaction; sp="evolution_complete"
    try:
        if owns: conn.execute("BEGIN IMMEDIATE")
        else: conn.execute(f"SAVEPOINT {sp}")
        obs_json=json.dumps(observations,sort_keys=True,separators=(",",":"),default=str)
        payload_json=json.dumps(dict(payload),sort_keys=True,separators=(",",":"),default=str)
        evidence_id=f"evidence:{provenance.execution_id}"
        conn.execute("INSERT OR IGNORE INTO evolution_evidence VALUES(?,?,?,?,?,?)",
            (evidence_id,provenance.execution_id,transition_id,provenance.evidence_digest,obs_json,payload_json))
        if failure_after=="evidence": raise RuntimeError("injected failure: evidence")
        row=conn.execute("SELECT evidence_digest,observations,transition_id FROM evolution_evidence WHERE evidence_id=?",(evidence_id,)).fetchone()
        if row is None or row!=(provenance.evidence_digest,obs_json,transition_id): raise RuntimeError("evidence verification failed")
        conn.execute("INSERT INTO evolution_transitions VALUES(?,?,?,?,?,?,?,?)",
            (transition_id,transition.candidate_id,transition.from_state_id,transition.to_state_id,provenance.provenance_id,"",provenance.evidence_digest,json.dumps(dict(persistable.payload()),sort_keys=True,separators=(",",":"),default=str)))
        if failure_after=="transition": raise RuntimeError("injected failure: transition")
        if conn.execute("SELECT provenance_id FROM evolution_provenance WHERE provenance_id=?",(provenance.provenance_id,)).fetchone() is not None:
            raise RuntimeError("conflicting replay for existing provenance")
        row=conn.execute("SELECT sequence,record_digest FROM evolution_audit ORDER BY sequence DESC LIMIT 1").fetchone()
        seq=0 if row is None else row[0]+1; prev="" if row is None else row[1]
        record=make_audit_record(sequence=seq,event_type=event_type,candidate_id=provenance.candidate_id,execution_id=provenance.execution_id,provenance_id=provenance.provenance_id,parent_state_digest=provenance.parent_state_digest,proposed_state_digest=provenance.proposed_state_digest,evidence_digest=provenance.evidence_digest,payload=dict(payload),previous_digest=prev)
        conn.execute("INSERT INTO evolution_provenance VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (provenance.provenance_id,provenance.execution_id,provenance.candidate_id,provenance.parent_state_id,provenance.parent_state_digest,provenance.proposed_state_digest,provenance.evidence_digest,provenance.evaluation_status,provenance.shadow_status,provenance.invariant_status,provenance.governance_decision,provenance.status,provenance.evolution_identity,provenance.proposed_state_content_id,provenance.candidate_binding_digest))
        if failure_after=="provenance": raise RuntimeError("injected failure: provenance")
        conn.execute("INSERT INTO evolution_audit VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (record.sequence,record.event_type,record.candidate_id,record.execution_id,record.provenance_id,record.parent_state_digest,record.proposed_state_digest,record.evidence_digest,record.payload_digest,record.previous_digest,record.record_digest))
        if failure_after=="audit": raise RuntimeError("injected failure: audit")
        conn.execute("UPDATE evolution_transitions SET audit_record_id=? WHERE transition_id=?",(record.record_digest,transition_id))
        if failure_after=="link": raise RuntimeError("injected failure: link")
        conn.commit() if owns else conn.execute(f"RELEASE SAVEPOINT {sp}")
        return DurableCommitResult(provenance.provenance_id,record)
    except Exception:
        if owns: conn.rollback()
        else: conn.execute(f"ROLLBACK TO SAVEPOINT {sp}"); conn.execute(f"RELEASE SAVEPOINT {sp}")
        raise
