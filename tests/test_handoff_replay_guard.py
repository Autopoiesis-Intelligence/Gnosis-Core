from registry.core_handoff import create_handoff
from registry.handoff_replay_guard import HandoffReplayGuard


def handoff():
    return create_handoff({"result":"AUTHORIZED","authorization_sha256":"a"*64},{"candidate_id":"c1","source_id":"s1","resource_id":"r1"},"core-evolution","propose",["e1"])["handoff"]


def test_first_consumption_is_accepted():
    h=handoff(); g=HandoffReplayGuard()
    assert g.consume(h["handoff_sha256"])["result"] == "ACCEPT"


def test_second_consumption_is_rejected_as_replay():
    h=handoff(); g=HandoffReplayGuard()
    g.consume(h["handoff_sha256"])
    assert g.consume(h["handoff_sha256"]) == {"result":"REJECT","errors":["handoff_replay"]}


def test_missing_digest_fails_closed():
    assert HandoffReplayGuard().consume("")["result"] == "REJECT"
