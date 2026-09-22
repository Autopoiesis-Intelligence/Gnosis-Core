"""Conservative aggregation of diagnostic evidence into candidate patterns.

Aggregation is deliberately weaker than causality: records sharing a common
case, state lineage, or provenance root are not treated as independent merely
because they repeat.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .provenance import DiagnosticEvidence


@dataclass(frozen=True)
class DiagnosticPattern:
    pattern_id: str
    case_id: str
    signature: str
    evidence_ids: tuple[str, ...]
    independent_sources: tuple[str, ...]
    repetition_count: int
    common_mode_flags: tuple[str, ...] = ()
    status: str = "CANDIDATE"


def _source(e: DiagnosticEvidence) -> str:
    refs = tuple(e.provenance_refs)
    for prefix in ("source:", "origin:", "agent:"):
        for ref in refs:
            if ref.startswith(prefix):
                return ref
    return refs[0] if refs else f"case:{e.case_id}"


def aggregate_diagnostic_patterns(
    evidence: Iterable[DiagnosticEvidence],
    *,
    minimum_repetitions: int = 2,
) -> tuple[DiagnosticPattern, ...]:
    if minimum_repetitions < 2:
        raise ValueError("minimum_repetitions must be >= 2")
    groups: dict[tuple[str, str], list[DiagnosticEvidence]] = {}
    for item in evidence:
        if item.lifecycle not in {"REPRODUCED", "VERIFIED", "DURABLE"}:
            continue
        signature = repr(sorted((str(k), repr(v)) for k, v in item.observations.items()))
        groups.setdefault((item.case_id, signature), []).append(item)

    patterns: list[DiagnosticPattern] = []
    for (case_id, signature), items in sorted(groups.items()):
        if len(items) < minimum_repetitions:
            continue
        sources = tuple(sorted({_source(e) for e in items}))
        flags = []
        if len(sources) == 1:
            flags.append("COMMON_SOURCE")
        state_ids = {e.state_id for e in items}
        if len(state_ids) == 1:
            flags.append("SAME_STATE")
        candidate_ids = {e.candidate_id for e in items}
        if len(candidate_ids) == 1:
            flags.append("SAME_CANDIDATE")
        pattern_id = f"pattern:{case_id}:{signature[:24]}"
        patterns.append(DiagnosticPattern(
            pattern_id, case_id, signature,
            tuple(e.evidence_id for e in items),
            sources, len(items), tuple(flags),
        ))
    return tuple(patterns)
