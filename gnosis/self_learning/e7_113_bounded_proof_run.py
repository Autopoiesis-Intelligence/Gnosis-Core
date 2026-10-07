"""E7.113 bounded, observe-only proof-run coordinator."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ProofState(str, Enum):
    PLANNED = "PLANNED"
    RUNNING = "RUNNING"
    PASSED = "PASSED"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class ProofRun:
    run_id: str
    target_commit_sha: str
    stages: tuple[str, ...]
    mutation_authorized: bool
    state: ProofState
    observations: tuple[str, ...]


REQUIRED_STAGES = (
    "E7.107",
    "E7.108",
    "E7.109",
    "E7.110",
    "E7.111",
    "E7.112",
)


def plan_proof_run(
    *, run_id: str, target_commit_sha: str, mutation_authorized: bool = False
) -> ProofRun:
    if not run_id or not target_commit_sha:
        raise ValueError("proof-run identity is required")
    if mutation_authorized:
        raise ValueError("bounded proof-run must be observe-only")
    return ProofRun(
        run_id,
        target_commit_sha,
        REQUIRED_STAGES,
        False,
        ProofState.PLANNED,
        (),
    )


def complete_proof_run(
    run: ProofRun, observations: tuple[str, ...], passed: bool
) -> ProofRun:
    if run.mutation_authorized:
        raise ValueError("mutation is forbidden")
    if not observations:
        return ProofRun(
            run.run_id,
            run.target_commit_sha,
            run.stages,
            False,
            ProofState.FAILED,
            (),
        )

    observed_stages = []
    for observation in observations:
        stage, separator, result = observation.partition(":")
        if not separator or stage not in run.stages:
            return ProofRun(
                run.run_id,
                run.target_commit_sha,
                run.stages,
                False,
                ProofState.FAILED,
                observations,
            )
        observed_stages.append((stage, result))

    if set(stage for stage, _ in observed_stages) != set(run.stages):
        return ProofRun(
            run.run_id,
            run.target_commit_sha,
            run.stages,
            False,
            ProofState.FAILED,
            observations,
        )

    if len(observed_stages) != len(set(stage for stage, _ in observed_stages)):
        return ProofRun(
            run.run_id,
            run.target_commit_sha,
            run.stages,
            False,
            ProofState.FAILED,
            observations,
        )

    state = ProofState.PASSED if passed and all(result == "PASS" for _, result in observed_stages) else ProofState.FAILED
    return ProofRun(
        run.run_id,
        run.target_commit_sha,
        run.stages,
        False,
        state,
        observations,
    )
