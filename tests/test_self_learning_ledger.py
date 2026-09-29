from dataclasses import replace

from gnosis.self_learning.ledger import chain_digest, create_event, verify_chain


def test_empty_chain():
    assert verify_chain([]) == (True, ())
    assert chain_digest([]) == "GENESIS"


def test_single_event_chain():
    event = create_event("candidate.created", "subject-1", {"value": 1})
    assert event.previous_event_digest == "GENESIS"
    assert verify_chain([event]) == (True, ())
    assert chain_digest([event]) == event.event_digest


def test_multi_event_chain():
    first = create_event("candidate.created", "subject-1", {"value": 1})
    second = create_event(
        "candidate.tested",
        "subject-1",
        {"value": 2},
        previous_event_digest=first.event_digest,
    )

    assert verify_chain([first, second]) == (True, ())
    assert chain_digest([first, second]) == second.event_digest


def test_payload_digest_tampering():
    event = create_event("candidate.created", "subject-1", {"value": 1})
    tampered = replace(event, payload_digest="sha256:" + "0" * 64)

    valid, errors = verify_chain([tampered])

    assert not valid
    assert any(error.startswith("EVENT_DIGEST_MISMATCH:") for error in errors)


def test_event_digest_tampering():
    event = create_event("candidate.created", "subject-1", {"value": 1})
    tampered = replace(
        event,
        event_digest="sha256:" + "0" * 64,
        event_id="sha256:" + "0" * 64,
    )

    valid, errors = verify_chain([tampered])

    assert not valid
    assert any(error.startswith("EVENT_DIGEST_MISMATCH:") for error in errors)


def test_previous_digest_tampering():
    first = create_event("candidate.created", "subject-1", {"value": 1})
    second = create_event(
        "candidate.tested",
        "subject-1",
        {"value": 2},
        previous_event_digest=first.event_digest,
    )
    tampered = replace(second, previous_event_digest="sha256:" + "0" * 64)

    valid, errors = verify_chain([first, tampered])

    assert not valid
    assert any(error.startswith("PREVIOUS_DIGEST_MISMATCH:") for error in errors)


def test_reordered_events():
    first = create_event("candidate.created", "subject-1", {"value": 1})
    second = create_event(
        "candidate.tested",
        "subject-1",
        {"value": 2},
        previous_event_digest=first.event_digest,
    )

    valid, errors = verify_chain([second, first])

    assert not valid
    assert any(error.startswith("PREVIOUS_DIGEST_MISMATCH:") for error in errors)


def test_missing_genesis():
    event = create_event(
        "candidate.created",
        "subject-1",
        {"value": 1},
        previous_event_digest="sha256:" + "1" * 64,
    )

    valid, errors = verify_chain([event])

    assert not valid
    assert any(error.startswith("PREVIOUS_DIGEST_MISMATCH:") for error in errors)
