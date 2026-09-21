# SQLite Persistence Adapter — R1.9

from __future__ import annotations

import sqlite3

from gnosis.core.types import Candidate, State, TransitionRecord
from gnosis.storage.repositories import (
    load_state,
    save_candidate,
    save_state,
)
from gnosis.ports.persistence import PersistencePort


class SQLitePersistenceAdapter(PersistencePort):
    """Compatibility adapter over the existing verified SQLite implementation."""

    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def save_state(self, state: State) -> None:
        save_state(self._conn, state)

    def load_state(self, state_id: str) -> State:
        return load_state(self._conn, state_id)

    def save_candidate(self, candidate: Candidate) -> None:
        save_candidate(self._conn, candidate)

    def record_transition(self, record: TransitionRecord) -> None:
        from gnosis.storage.repositories import save_transition
        save_transition(self._conn, record)
