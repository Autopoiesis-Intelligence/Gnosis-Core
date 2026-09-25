from registry.core_handoff import create_handoff, digest


def authorized():
    return {"result":"AUTHORIZED","authorization_sha256":"a"*64}


def candidate():
    return {"candidate_id":"c1","source_id":"science-math","resource_id":"r1"}


def test_handoff_digest_covers_security_relevant_fields():
    out=create_handoff(authorized(),candidate(),"core-evolution","propose",["e1"])
    h=out["handoff"]
    unsigned=dict(h)
    unsigned.pop("handoff_sha256")
    assert h["handoff_sha256"] == digest(unsigned)


def test_candidate_substitution_changes_handoff_digest():
    out=create_handoff(authorized(),candidate(),"core-evolution","propose",["e1"])
    h=out["handoff"]
    tampered=dict(h, candidate_id="c2")
    assert digest(tampered) != h["handoff_sha256"]


def test_source_substitution_changes_handoff_digest():
    out=create_handoff(authorized(),candidate(),"core-evolution","propose",["e1"])
    h=out["handoff"]
    tampered=dict(h, source_id="foreign-source")
    assert digest(tampered) != h["handoff_sha256"]


def test_evidence_substitution_changes_handoff_digest():
    out=create_handoff(authorized(),candidate(),"core-evolution","propose",["e1"])
    h=out["handoff"]
    tampered=dict(h, evidence_refs=["forged-evidence"])
    assert digest(tampered) != h["handoff_sha256"]


def test_authorization_substitution_changes_handoff_digest():
    out=create_handoff(authorized(),candidate(),"core-evolution","propose",["e1"])
    h=out["handoff"]
    tampered=dict(h, federation_authorization_sha256="b"*64)
    assert digest(tampered) != h["handoff_sha256"]


def test_target_and_action_substitution_changes_handoff_digest():
    out=create_handoff(authorized(),candidate(),"core-evolution","propose",["e1"])
    h=out["handoff"]
    assert digest(dict(h, target="other-target")) != h["handoff_sha256"]
    assert digest(dict(h, action="commit")) != h["handoff_sha256"]
