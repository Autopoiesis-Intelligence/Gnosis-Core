from dataclasses import dataclass
from enum import Enum

from gnosis.self_learning.e7_113_ci_entrypoint import _serialize


class State(str, Enum):
    PASS = "PASS"


@dataclass(frozen=True)
class Nested:
    state: State
    values: tuple[str, ...]


def test_serialize_is_json_safe_and_preserves_enum_values():
    value = Nested(State.PASS, ("stdout", "stderr"))
    assert _serialize(value) == {"state": "PASS", "values": ["stdout", "stderr"]}
