"""Small, authority-free state machine for the Core autopoietic runtime."""
from __future__ import annotations
from dataclasses import dataclass

STAGES = (
    "DIAGNOSE", "INVESTIGATE", "PROPOSE",
    "SHADOW", "GOVERN", "COMMIT", "DONE",
)

NEXT = {
    "DIAGNOSE": "INVESTIGATE",
    "INVESTIGATE": "PROPOSE",
    "PROPOSE": "SHADOW",
    "SHADOW": "GOVERN",
    "GOVERN": "COMMIT",
    "COMMIT": "DONE",
}

@dataclass(frozen=True)
class AutopoiesisRuntime:
    stage: str = "DIAGNOSE"
    cycle_id: str = ""

    def advance(self, completed_stage: str) -> "AutopoiesisRuntime":
        if self.stage == "DONE":
            raise ValueError("runtime cycle is already complete")
        if completed_stage != self.stage:
            raise ValueError("completed stage does not match runtime stage")
        return AutopoiesisRuntime(NEXT[self.stage], self.cycle_id)

    def can_commit(self) -> bool:
        return self.stage == "COMMIT"

    def require_stage(self, expected: str) -> None:
        if self.stage != expected:
            raise ValueError(f"runtime is at {self.stage}, expected {expected}")
