"""Canonical execution input provenance bound to a State identity."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

from gnosis.core.types import State, _stable_hash
from gnosis.core.state_identity import state_digest


@dataclass(frozen=True)
class ExecutionInput:
    input_type: str
    state_id: str
    state_digest: str
    content_digest: str

    def canonical_payload(self) -> dict[str, str]:
        return {
            "content_digest": self.content_digest,
            "input_type": self.input_type,
            "state_digest": self.state_digest,
            "state_id": self.state_id,
        }

    @property
    def digest(self) -> str:
        payload = json.dumps(
            self.canonical_payload(),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def execution_input_from_state(state: State, input_type: str = "state") -> ExecutionInput:
    return ExecutionInput(
        input_type=input_type,
        state_id=state.state_id,
        state_digest=state_digest(state),
        content_digest=_stable_hash(state),
    )


def verify_execution_input(
    expected: ExecutionInput, state: State, input_type: str = "state"
) -> bool:
    return expected == execution_input_from_state(state, input_type)
