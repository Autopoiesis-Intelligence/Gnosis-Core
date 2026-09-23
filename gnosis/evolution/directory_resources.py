"""Explicit resource delta for directory shadow evaluation."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DirectoryResourceSnapshot:
    file_count: int
    byte_count: int
    estimated_work_units: int = 0


@dataclass(frozen=True)
class DirectoryResourceDelta:
    files: int
    bytes: int
    work_units: int

    @property
    def non_worsening(self) -> bool:
        return self.files <= 0 and self.bytes <= 0 and self.work_units <= 0


def calculate_resource_delta(
    before: DirectoryResourceSnapshot,
    after: DirectoryResourceSnapshot,
) -> DirectoryResourceDelta:
    """Calculate explicit deltas; this function performs no measurement or mutation."""
    return DirectoryResourceDelta(
        files=after.file_count - before.file_count,
        bytes=after.byte_count - before.byte_count,
        work_units=after.estimated_work_units - before.estimated_work_units,
    )
