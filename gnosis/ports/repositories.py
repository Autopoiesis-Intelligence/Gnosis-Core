from __future__ import annotations

from typing import Protocol

from gnosis.core import Candidate, State, TransitionRecord
from gnosis.instances.instance import Instance


class StateRepository(Protocol):
    """Durable instance/state boundary; no SQL types leak through it."""

    def save_instance(self, instance: Instance) -> None: ...
    def load_instance(self, instance_id: str) -> Instance: ...
    def save_state(self, state: State) -> None: ...
    def load_state(self, state_id: str) -> State: ...
    def save_candidate(self, candidate: Candidate) -> None: ...
    def load_candidate(self, candidate_id: str) -> Candidate: ...


class EvolutionRepository(Protocol):
    """Canonical transition/recovery semantics."""

    def persist_transition(
        self,
        instance: Instance,
        candidate: Candidate,
        record: TransitionRecord,
        *,
        actor: str,
        failure_at: str | None = None,
    ) -> None: ...

    def load_transition_records(
        self, instance_id: str | None = None
    ) -> list[TransitionRecord]: ...

    def verify_durable_graph(self) -> tuple[int, str]: ...
    def recover_instance(self, instance_id: str) -> Instance: ...


class ReflectionRepository(Protocol):
    """Durable analytical evidence; never canonical Ψ state."""

    def save_reflection_report(self, report: object, *, created_at: str, shadow_assessments: tuple[object, ...] = ()) -> str: ...
    def load_reflection_report(self, report_id: str) -> dict: ...
    def list_reflection_reports(self) -> tuple[dict, ...]: ...


class EvolutionMemoryRepository(Protocol):
    """Append-only endogenous evolution memory; observational evidence only."""

    def append_evolution_memory(self, *, instance_id: str, candidate_id: str, transition_id: str, state_id: str, proposal_id: str | None, outcome: str, evidence: tuple[str, ...] | list[str], created_at: str | None = None) -> object: ...
    def load_evolution_memory(self, instance_id: str, *, limit: int = 100) -> tuple[object, ...]: ...


class AuditRepository(Protocol):
    """Append-only evidence and integrity verification."""

    def append_audit(
        self,
        *,
        actor: str,
        action: str,
        resource: str,
        result: str,
        timestamp: str | None = None,
        event_key: str | None = None,
        transition_id_value: str | None = None,
    ) -> str: ...

    def verify_audit_chain(self) -> tuple[int, str]: ...
