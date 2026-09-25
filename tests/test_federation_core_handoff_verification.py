from registry.core_handoff import create_handoff, verify_handoff


def make():
    return create_handoff({"result":"AUTHORIZED","authorization_sha256":"a"*64},{"candidate_id":"c1","source_id":"s1","resource_id":"r1"},"core-evolution","propose",["e1"])["handoff"]


def test_valid_handoff_is_accepted():
    assert verify_handoff(make())["result"] == "VALID"


def test_tampered_candidate_is_rejected():
    h=make(); h["candidate_id"]="c2"
    assert verify_handoff(h) == {"result":"REJECT","errors":["handoff_digest_mismatch"]}


def test_tampered_evidence_is_rejected():
    h=make(); h["evidence_refs"]=["forged"]
    assert verify_handoff(h)["result"] == "REJECT"


def test_missing_digest_is_rejected():
    h=make(); h.pop("handoff_sha256")
    assert verify_handoff(h)["result"] == "REJECT"


def test_committed_status_is_rejected_at_federation_boundary():
    h=make(); h["status"]="COMMITTED"
    h["handoff_sha256"] = __import__("registry.core_handoff",fromlist=["digest"]).digest({k:v for k,v in h.items() if k!="handoff_sha256"})
    assert verify_handoff(h)["result"] == "REJECT"
