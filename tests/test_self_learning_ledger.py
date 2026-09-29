from dataclasses import replace

from gnosis.self_learning.ledger import create_event, verify_chain, chain_digest


def test_empty_chain() -> None:
    assert verify_chain([]) == (True, ())
    assert chain_digest([]) == "GENESIS"


def test_single_event_chain() -> None:
    event = create_event("PROPOSAL", "p1", {"x": 1})
    assert event.previous_event_digest == "GENESIS"
    assert verify_chain([event]) == (True, ())
    assert chain_digest([event]) == event.event_digest


def test_multi_event_chain() -> None:
    first = create_event("PROPOSAL", "p1", {"x": 1})
    second = create_event("VALIDATION", "p1", {"valid": True}, first.event_digest)
    third = create_event("COMMIT", "p1", {"committed": True}, second.event_digest)
    assert verify_chain([first, second, third]) == (True, ())
    assert chain_digest([first, second, third]) == third.event_digest


def test_payload_digest_tampering() -> None:
    first = create_event("PROPOSAL", "p1", {"x": 1})
    second = create_event("VALIDATION", "p1", {"valid": True}, first.event_digest)
    tampered = replace(second, payload_digest="sha256:tampered")
    ok, errors = verify_chain([first, tampered])
    assert not ok
    assert any(error.startswith("EVENT_DIGEST_MISMATCH") for error in errors)


def test_event_digest_tampering() -> None:
    event = create_event("PROPOSAL", "p1", {"x": 1})
    tampered = replace(event, event_digest="sha256:tampered")
    ok, errors = verify_chain([tampered])
    assert not ok
    assert any(error.startswith("EVENT_DIGEST_MISMATCH") for error in errors)


def test_previous_digest_tampering() -> None:
    first = create_event("PROPOSAL", "p1", {"x": 1})
    second = create_event("VALIDATION", "p1", {"valid": True}, first.event_digest)
    tampered = replace(second, previous_event_digest="sha256:tampered")
    ok, errors = verify_chain([first, tampered])
    assert not ok
    assert any(error.startswith("PREVIOUS_DIGEST_MISMATCH") for error in errors)


def test_reordered_events() -> None:
    first = create_event("PROPOSAL", "p1", {"x": 1})
    second = create_event("VALIDATION", "p1", {"valid": True}, first.event_digest)
    ok, errors = verify_chain([second, first])
    assert not ok
    assert errors


def test_missing_genesis() -> None:
    event = create_event("PROPOSAL", "p1", {"x": 1})
    tampered = replace(event, previous_event_digest="sha256:not-genesis")
    ok, errors = verify_chain([tampered])
    assert not ok
    assert any(error.startswith("PREVIOUS_DIGEST_MISMATCH") for error in errors)


def test_chain_is_hash_linked() -> None:
    first = create_event("PROPOSAL", "p1", {"x": 1})
    second = create_event("VALIDATION", "p1", {"valid": True}, first.event_digest)
    assert verify_chain([first, second]) == (True, ())
    assert chain_digest([first, second]) == second.event_digest


def test_tampering_breaks_chain() -> None:
    first = create_event("PROPOSAL", "p1", {"x": 1})
    second = create_event("VALIDATION", "p1", {"valid": True}, first.event_digest)
    tampered = replace(second, payload_digest="sha256:tampered")
    ok, errors = verify_chain([first, tampered])
    assert not ok
    assert errors


def test_genesis_chain() -> None:
    event = create_event("DATABASE", "db1", {"count": 1})
    assert event.previous_event_digest == "GENESIS"


def test_authority_tampering_breaks_chain() -> None:
    event = create_event("PROPOSAL", "p-authority", {"x": 1})
    tampered = replace(event, authority="attacker-controlled-authority")
    ok, errors = verify_chain([tampered])
    assert not ok
    assert any(x.startswith("EVENT_DIGEST_MISMATCH") for x in errors)
