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


def test_main_returns_nonzero_for_failed_proof(monkeypatch, tmp_path):
    from gnosis.self_learning import e7_113_ci_entrypoint as entry

    class FakeRun:
        class Proof:
            state = type("State", (), {"value": "FAILED"})()
        proof_run = Proof()

    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("GITHUB_SHA", "a" * 40)
    monkeypatch.setenv("GITHUB_REF", "refs/heads/test")
    monkeypatch.setenv("GITHUB_REPOSITORY", "owner/repo")
    monkeypatch.setattr(entry, "run_bounded_proof", lambda **kwargs: FakeRun())
    monkeypatch.setattr(entry, "create_selection_record", lambda **kwargs: type("Selection", (), {"selection_record_id": "s", "integrity_digest": "d", "candidates": (type("Candidate", (), {"implementation_paths": ()})(),)})())
    monkeypatch.setattr(entry, "create_scope_lock", lambda **kwargs: object())
    assert entry.main() == 1
