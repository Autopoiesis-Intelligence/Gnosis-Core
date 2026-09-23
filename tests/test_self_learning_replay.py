from gnosis.self_learning.ledger import create_event
from gnosis.self_learning.replay import replay

def test_replay_reconstructs_valid_chain():
    a = create_event("DATABASE", "flow-1", {"x": 1})
    b = create_event("PROPOSAL", "flow-1", {"x": 2}, a.event_digest)
    c = create_event("VALIDATION", "flow-1", {"x": 3}, b.event_digest)
    result = replay([a, b, c], expected_subject_id="flow-1")
    assert result.complete is True
    assert result.ordered_event_ids == (a.event_id, b.event_id, c.event_id)

def test_replay_detects_subject_mixing():
    a = create_event("DATABASE", "flow-1", {"x": 1})
    b = create_event("PROPOSAL", "flow-2", {"x": 2}, a.event_digest)
    result = replay([a, b], expected_subject_id="flow-1")
    assert result.complete is False
    assert any(x.startswith("SUBJECT_MISMATCH") for x in result.errors)

def test_replay_detects_broken_chain():
    a = create_event("DATABASE", "flow-1", {"x": 1})
    b = create_event("PROPOSAL", "flow-1", {"x": 2}, "sha256:wrong")
    result = replay([a, b])
    assert result.complete is False


def test_replay_rejects_tampered_event_digest() -> None:
    from dataclasses import replace

    event = create_event("DATABASE", "flow-tamper", {"x": 1})
    tampered = replace(event, event_digest="sha256:tampered")
    result = replay([tampered], expected_subject_id="flow-tamper")
    assert result.complete is False
    assert any(x.startswith("EVENT_DIGEST_MISMATCH") for x in result.errors)
