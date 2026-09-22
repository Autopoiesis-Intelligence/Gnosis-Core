"""Lineage-aware qualification of diagnostic evidence sources."""
from __future__ import annotations

from dataclasses import dataclass
from gnosis.evidence.provenance import DiagnosticEvidence


@dataclass(frozen=True)
class EvidenceLineage:
    evidence_id: str
    source: str
    lineage: str
    execution: str
    test_rule: str
    mechanism: str


@dataclass(frozen=True)
class LineageQualification:
    independent_groups: tuple[tuple[str, ...], ...]
    common_mode_reasons: tuple[str, ...]


def _ref(e: DiagnosticEvidence, prefix: str) -> str:
    for r in e.provenance_refs:
        if r.startswith(prefix):
            return r
    return ""


def qualify_lineage(evidence: tuple[DiagnosticEvidence, ...]) -> LineageQualification:
    groups: dict[tuple[str, str, str, str], list[str]] = {}
    reasons: set[str] = set()
    for e in evidence:
        source = _ref(e, "source:") or _ref(e, "origin:") or f"case:{e.case_id}"
        lineage = _ref(e, "lineage:")
        execution = _ref(e, "execution:")
        rule = _ref(e, "test-rule:")
        mechanism = _ref(e, "mechanism:")
        key = (lineage, execution, rule, mechanism)
        groups.setdefault(key, []).append(e.evidence_id)
        if lineage or execution or rule or mechanism:
            reasons.update(
                x for x, value in (
                    ("SHARED_LINEAGE", lineage),
                    ("SHARED_EXECUTION", execution),
                    ("SHARED_TEST_RULE", rule),
                    ("SHARED_MECHANISM", mechanism),
                ) if value
            )
    # Empty provenance dimensions are unknown, not proof of independence.
    independent = []
    for key, ids in groups.items():
        if key != ("", "", "", ""):
            independent.append(tuple(ids))
        else:
            independent.append(tuple(ids))
    return LineageQualification(tuple(independent), tuple(sorted(reasons)))
