"""Cycle lineage binding for the Core autopoietic runtime."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Mapping

REQUIRED = {
    "DIAGNOSE": "gap_id",
    "INVESTIGATE": "investigation_id",
    "PROPOSE": "proposal_id",
    "SHADOW": "evaluation_id",
    "GOVERN": "authorization_id",
    "COMMIT": "transition_id",
}

@dataclass(frozen=True)
class LineageArtifact:
    stage: str
    cycle_id: str
    artifact_id: str
    parent_artifact_id: str | None = None

def validate_lineage(current_stage: str, cycle_id: str, artifact: LineageArtifact, expected_parent: str | None) -> None:
    if artifact.stage != current_stage:
        raise ValueError("artifact stage mismatch")
    if artifact.cycle_id != cycle_id:
        raise ValueError("artifact belongs to another cycle")
    if not artifact.artifact_id:
        raise ValueError("artifact identity is required")
    if artifact.parent_artifact_id != expected_parent:
        raise ValueError("artifact parent lineage mismatch")
    if current_stage not in REQUIRED:
        raise ValueError("unknown runtime stage")

@dataclass(frozen=True)
class LineageRuntime:
    stage: str = "DIAGNOSE"
    cycle_id: str = ""
    last_artifact_id: str | None = None

    def advance(self, artifact: LineageArtifact) -> "LineageRuntime":
        validate_lineage(self.stage, self.cycle_id, artifact, self.last_artifact_id)
        next_stage = {
            "DIAGNOSE": "INVESTIGATE",
            "INVESTIGATE": "PROPOSE",
            "PROPOSE": "SHADOW",
            "SHADOW": "GOVERN",
            "GOVERN": "COMMIT",
            "COMMIT": "DONE",
        }[self.stage]
        return LineageRuntime(next_stage, self.cycle_id, artifact.artifact_id)
