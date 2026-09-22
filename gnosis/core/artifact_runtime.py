"""Artifact-backed progression for the Core autopoietic runtime."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Mapping

REQUIRED_ARTIFACT = {
    "DIAGNOSE": "gap_id",
    "INVESTIGATE": "investigation_id",
    "PROPOSE": "proposal_id",
    "SHADOW": "evaluation_id",
    "GOVERN": "authorization_id",
    "COMMIT": "transition_id",
}

@dataclass(frozen=True)
class RuntimeArtifact:
    stage: str
    refs: Mapping[str, str]

def validate_artifact(stage: str, artifact: RuntimeArtifact) -> None:
    if artifact.stage != stage:
        raise ValueError("artifact stage mismatch")
    required = REQUIRED_ARTIFACT.get(stage)
    if required is None:
        raise ValueError("unknown runtime stage")
    value = artifact.refs.get(required)
    if not value:
        raise ValueError(f"{stage} requires artifact reference: {required}")

@dataclass(frozen=True)
class ArtifactBackedRuntime:
    stage: str = "DIAGNOSE"
    cycle_id: str = ""

    def advance(self, artifact: RuntimeArtifact) -> "ArtifactBackedRuntime":
        validate_artifact(self.stage, artifact)
        next_stage = {
            "DIAGNOSE": "INVESTIGATE",
            "INVESTIGATE": "PROPOSE",
            "PROPOSE": "SHADOW",
            "SHADOW": "GOVERN",
            "GOVERN": "COMMIT",
            "COMMIT": "DONE",
        }[self.stage]
        return ArtifactBackedRuntime(next_stage, self.cycle_id)
