from gnosis.core.rule_identity import rule_identity, verify_rule_identity

def test_rule_identity_round_trip():
    i=rule_identity("rule:1",{"predicate":"x>0","version":1})
    assert verify_rule_identity(i,{"predicate":"x>0","version":1})

def test_rule_content_tamper_is_detected():
    i=rule_identity("rule:1",{"predicate":"x>0","version":1})
    assert not verify_rule_identity(i,{"predicate":"x>=0","version":1})

def test_rule_id_change_is_detected():
    i=rule_identity("rule:1",{"predicate":"x>0"})
    assert not verify_rule_identity(i,{"predicate":"x>0","version":2})
