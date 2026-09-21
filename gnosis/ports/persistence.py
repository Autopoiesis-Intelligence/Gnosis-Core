# Persistence Port — R1.9

from __future__ import annotations

from typing import Protocol

from gnosis.core.types import Candidate, State, TransitionRecord


class PersistencePort(Protocol):
    """Minimal semantic persistence contract for Core consumers.

    Implementations must preserve integrity, idempotency and recovery semantics.
    This protocol deliberately exposes no SQLite-specific types.
    """

    def save_state(self, state: State) -> None: ...

    def load_state(self, state_id: str) -> State: ...

    def save_candidate(self, candidate: Candidate) -> None: ...

    def record_transition(self, record: TransitionRecord) -> None: ...
