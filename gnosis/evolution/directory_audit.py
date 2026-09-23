"""Audit bridge for directory optimization provenance.

This module creates no audit authority of its own. It only adapts the
existing append-only audit record contract and fail-closed cross-check.
"""
from __future__ import annotations

from .audit import EvolutionAuditRecord, ProvenanceAuditCrossCheck, crosscheck_provenance_audit
from .directory_candidate import OptimizationCandidate
from .directory_provenance import build_directory_provenance


def crosscheck_directory_provenance_audit(
    candidate: OptimizationCandidate,
    provenance,
    audit_record: EvolutionAuditRecord,
) -> ProvenanceAuditCrossCheck:
    """Verify that the directory candidate, provenance and audit record agree."""
    if provenance.candidate_id != candidate.candidate_id:
        return ProvenanceAuditCrossCheck(False, ("candidate/provenance identity mismatch",))
    if provenance.candidate_binding_digest != candidate.candidate_binding_digest:
        return ProvenanceAuditCrossCheck(False, ("candidate binding mismatch",))
    return crosscheck_provenance_audit(provenance, audit_record)
