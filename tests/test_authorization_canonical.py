from gnosis.reflection.crypto import canonical_owner_authorization

def payload():
    return {
        "authority_root": "owner-root",
        "scope": "bounded",
        "policy_version": "p1",
        "evidence_digest": "e1",
        "request_provenance": "r1",
        "evolution_identity": "ev1",
        "approval_id": "a1",
    }

def test_canonicalization_is_deterministic():
    assert canonical_owner_authorization(payload()) == canonical_owner_authorization(dict(reversed(list(payload().items()))))

def test_relevant_field_change_changes_payload():
    a = payload()
    b = payload()
    b["scope"] = "different"
    assert canonical_owner_authorization(a) != canonical_owner_authorization(b)

def test_extra_or_missing_field_is_rejected():
    a = payload()
    a.pop("scope")
    try:
        canonical_owner_authorization(a)
    except ValueError:
        pass
    else:
        raise AssertionError("missing field accepted")
