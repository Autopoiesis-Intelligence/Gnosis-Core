from __future__ import annotations

import sqlite3

from gnosis.core import Candidate, State, TransitionRecord
from gnosis.instances.instance import Instance
from gnosis.ports.repositories import AuditRepository, EvolutionMemoryRepository, EvolutionRepository, ReflectionRepository, StateRepository
from gnosis.storage.repositories import (
    append_audit,
    load_candidate,
    load_state,
    load_transition_records,
    persist_transition,
    recover_instance,
    save_candidate,
    save_instance,
    save_state,
    verify_audit_chain,
    verify_durable_graph,
    load_instance,
    append_evolution_memory,
    load_evolution_memory,
)


class SQLiteStateRepository(StateRepository):
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def save_instance(self, instance: Instance) -> None:
        save_instance(self._conn, instance)

    def load_instance(self, instance_id: str) -> Instance:
        from gnosis.storage.repositories import load_instance
        return load_instance(self._conn, instance_id)

    def save_state(self, state: State) -> None:
        save_state(self._conn, state)

    def load_state(self, state_id: str) -> State:
        return load_state(self._conn, state_id)

    def save_candidate(self, candidate: Candidate) -> None:
        save_candidate(self._conn, candidate)

    def load_candidate(self, candidate_id: str) -> Candidate:
        return load_candidate(self._conn, candidate_id)


class SQLiteEvolutionRepository(EvolutionRepository):
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def persist_transition(
        self,
        instance: Instance,
        candidate: Candidate,
        record: TransitionRecord,
        *,
        actor: str,
        failure_at: str | None = None,
    ) -> None:
        persist_transition(
            self._conn,
            instance,
            candidate,
            record,
            actor=actor,
            failure_at=failure_at,
        )

    def load_transition_records(
        self, instance_id: str | None = None
    ) -> list[TransitionRecord]:
        return load_transition_records(self._conn, instance_id)

    def verify_durable_graph(self) -> tuple[int, str]:
        return verify_durable_graph(self._conn)

    def recover_instance(self, instance_id: str) -> Instance:
        return recover_instance(self._conn, instance_id)


class SQLiteEvolutionMemoryRepository(EvolutionMemoryRepository):
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def append_evolution_memory(self, **kwargs):
        return append_evolution_memory(self._conn, **kwargs)

    def load_evolution_memory(self, instance_id: str, *, limit: int = 100):
        return load_evolution_memory(self._conn, instance_id, limit=limit)


class SQLiteReflectionRepository(ReflectionRepository):
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def save_reflection_report(self, report, *, created_at: str, shadow_assessments=()):
        from gnosis.reflection.persistence import save_reflection_report
        return save_reflection_report(self._conn, report, created_at=created_at, shadow_assessments=shadow_assessments)

    def load_reflection_report(self, report_id: str):
        from gnosis.reflection.persistence import load_reflection_report
        return load_reflection_report(self._conn, report_id)

    def list_reflection_reports(self):
        from gnosis.reflection.persistence import list_reflection_reports
        return list_reflection_reports(self._conn)


class SQLiteAuditRepository(AuditRepository):
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

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
    ) -> str:
        return append_audit(
            self._conn,
            actor=actor,
            action=action,
            resource=resource,
            result=result,
            timestamp=timestamp,
            event_key=event_key,
            transition_id_value=transition_id_value,
        )

    def verify_audit_chain(self) -> tuple[int, str]:
        return verify_audit_chain(self._conn)
