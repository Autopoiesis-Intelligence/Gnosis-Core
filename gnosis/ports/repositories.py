from __future__ import annotations

from typing import Protocol

from gnosis.core import Candidate, State, TransitionRecord
from gnosis.instances.instance import Instance


class StateRepository(Protocol):
    def save_state(self, state: State) -> None: ...
    def load_state(self, state_id: str) -> State: ...
    def save_candidate(self, candidate: Candidate) -> None: ...
    def load_candidate(self, candidate_id: str) -> Candidate: ...


class EvolutionRepository(Protocol):
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


class AuditRepository(Protocol):
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
