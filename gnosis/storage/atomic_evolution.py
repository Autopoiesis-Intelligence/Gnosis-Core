"""Atomic persistence adapter for complete evolution evidence."""
from __future__ import annotations
import json, sqlite3
from typing import Any, Mapping
from gnosis.core.audit import EvolutionAuditRecord, make_audit_record
from gnosis.core.provenance import EvidenceProvenance, canonical_digest
from gnosis.core.durable_commit import DurableCommitResult

def persist_evolution_with_evidence(conn: sqlite3.Connection, provenance: EvidenceProvenance, *,
    event_type: str, payload: Mapping[str, Any], transition_id: str,
    observations: Mapping[str, Any]) -> DurableCommitResult:
    if canonical_digest(observations) != provenance.evidence_digest:
        raise ValueError("evidence digest does not match observations")
    owns=not conn.in_transaction; sp="evolution_complete"
    try:
        if owns: conn.execute("BEGIN IMMEDIATE")
        else: conn.execute(f"SAVEPOINT {sp}")
        evidence_id=f"evidence:{provenance.execution_id}"
        obs_json=json.dumps(observations,sort_keys=True,separators=(",",":"),default=str)
        payload_json=json.dumps(dict(payload),sort_keys=True,separators=(",",":"),default=str)
        conn.execute("INSERT OR IGNORE INTO evolution_evidence(evidence_id,execution_id,transition_id,evidence_digest,observations,created_payload) VALUES(?,?,?,?,?,?)",
                     (evidence_id,provenance.execution_id,transition_id,provenance.evidence_digest,obs_json,payload_json))
        row=conn.execute("SELECT evidence_digest,observations,transition_id FROM evolution_evidence WHERE evidence_id=?",(evidence_id,)).fetchone()
        if row is None or row[0]!=provenance.evidence_digest or row[1]!=obs_json or row[2]!=transition_id:
            raise RuntimeError("evidence persistence verification failed")
        existing=conn.execute("SELECT provenance_id,execution_id,candidate_id,parent_state_digest,proposed_state_digest,evidence_digest,evolution_identity,proposed_state_content_id,candidate_binding_digest FROM evolution_provenance WHERE provenance_id=?",(provenance.provenance_id,)).fetchone()
        if existing is None:
            row=conn.execute("SELECT sequence,record_digest FROM evolution_audit ORDER BY sequence DESC LIMIT 1").fetchone()
            seq=0 if row is None else row[0]+1; prev="" if row is None else row[1]
            record=make_audit_record(sequence=seq,event_type=event_type,candidate_id=provenance.candidate_id,execution_id=provenance.execution_id,provenance_id=provenance.provenance_id,parent_state_digest=provenance.parent_state_digest,proposed_state_digest=provenance.proposed_state_digest,evidence_digest=provenance.evidence_digest,payload=dict(payload),previous_digest=prev)
            conn.execute("INSERT INTO evolution_provenance (provenance_id,execution_id,candidate_id,parent_state_id,parent_state_digest,proposed_state_digest,evidence_digest,evaluation_status,shadow_status,invariant_status,governance_decision,status,evolution_identity,proposed_state_content_id,candidate_binding_digest) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (provenance.provenance_id,provenance.execution_id,provenance.candidate_id,provenance.parent_state_id,provenance.parent_state_digest,provenance.proposed_state_digest,provenance.evidence_digest,provenance.evaluation_status,provenance.shadow_status,provenance.invariant_status,provenance.governance_decision,provenance.status,provenance.evolution_identity,provenance.proposed_state_content_id,provenance.candidate_binding_digest))
            conn.execute("INSERT INTO evolution_audit (sequence,event_type,candidate_id,execution_id,provenance_id,parent_state_digest,proposed_state_digest,evidence_digest,payload_digest,previous_digest,record_digest) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                (record.sequence,record.event_type,record.candidate_id,record.execution_id,record.provenance_id,record.parent_state_digest,record.proposed_state_digest,record.evidence_digest,record.payload_digest,record.previous_digest,record.record_digest))
        else:
            expected=(provenance.provenance_id,provenance.execution_id,provenance.candidate_id,provenance.parent_state_digest,provenance.proposed_state_digest,provenance.evidence_digest,provenance.evolution_identity,provenance.proposed_state_content_id,provenance.candidate_binding_digest)
            if existing!=expected: raise RuntimeError("conflicting replay for existing provenance")
            record_row=conn.execute("SELECT sequence,event_type,candidate_id,execution_id,provenance_id,parent_state_digest,proposed_state_digest,evidence_digest,payload_digest,previous_digest,record_digest FROM evolution_audit WHERE provenance_id=?",(provenance.provenance_id,)).fetchone()
            if record_row is None: raise RuntimeError("existing provenance has no audit record")
            record=EvolutionAuditRecord(*record_row)
        conn.commit() if owns else conn.execute(f"RELEASE SAVEPOINT {sp}")
        return DurableCommitResult(provenance.provenance_id,record)
    except Exception:
        if owns: conn.rollback()
        else:
            conn.execute(f"ROLLBACK TO SAVEPOINT {sp}"); conn.execute(f"RELEASE SAVEPOINT {sp}")
        raise
