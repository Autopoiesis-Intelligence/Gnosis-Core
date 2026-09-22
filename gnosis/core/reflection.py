"""Canonical Core reflection input derived from diagnostic gaps."""
from __future__ import annotations

from dataclasses import dataclass

from .gap import GapHypothesis


@dataclass(frozen=True)
class ReflectionFinding:
    finding_id: str
    gap_id: str
    source_records: tuple[str, ...]
    statement: str
    conditions: tuple[str, ...]
    counterevidence: tuple[str, ...]
    status: str = "OPEN"
    provenance: str = "core-reflection"

    @classmethod
    def from_gap(cls, gap: GapHypothesis) -> "ReflectionFinding":
        if gap.status != "HYPOTHESIS":
            raise ValueError("only gap hypotheses can enter reflection")
        if not gap.source_records:
            raise ValueError("reflection requires source records")
        return cls(
            finding_id="finding:" + gap.gap_id.removeprefix("gap:"),
            gap_id=gap.gap_id,
            source_records=gap.source_records,
            statement=gap.description,
            conditions=gap.conditions,
            counterevidence=gap.counterevidence,
        )
