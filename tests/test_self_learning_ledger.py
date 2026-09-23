from gnosis.self_learning.ledger import create_event, verify_chain, chain_digest

def test_chain_is_hash_linked():
    a=create_event("PROPOSAL","p1",{"x":1})
    b=create_event("VALIDATION","p1",{"valid":True},a.event_digest)
    assert verify_chain([a,b])==(True,())
    assert chain_digest([a,b])==b.event_digest

def test_tampering_breaks_chain():
    a=create_event("PROPOSAL","p1",{"x":1})
    b=create_event("VALIDATION","p1",{"valid":True},a.event_digest)
    tampered=type(b)(b.event_id,b.event_type,b.subject_id,"sha256:tampered",b.previous_event_digest,b.event_digest,b.provenance,b.authority)
    ok,errors=verify_chain([a,tampered])
    assert not ok
    assert errors

def test_genesis_chain():
    a=create_event("DATABASE","db1",{"count":1})
    assert a.previous_event_digest=="GENESIS"


def test_authority_tampering_breaks_chain() -> None:
    from dataclasses import replace

    event = create_event("PROPOSAL", "p-authority", {"x": 1})
    tampered = replace(event, authority="attacker-controlled-authority")
    ok, errors = verify_chain([tampered])
    assert not ok
    assert any(x.startswith("EVENT_DIGEST_MISMATCH") for x in errors)
