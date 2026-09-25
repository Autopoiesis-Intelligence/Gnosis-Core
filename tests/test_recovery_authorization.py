import pytest

from gnosis.storage.authorization import (
    AuthorizationError,
    RecoveryAuthorization,
    validate_recovery_authorization,
)


def auth(**overrides):
    values = {
        "authorization_id": "auth-1",
        "subject": "instance-1",
        "requested_by": "principal-1",
        "authority": "governance/recovery",
        "decision": "allow",
        "reason": "recovery",
        "issued_at": "2026-09-25T00:00:00Z",
        "expires_at": "2026-09-26T00:00:00Z",
        "evidence_digest": "evidence-1",
    }
    values.update(overrides)
    return RecoveryAuthorization(**values)


def test_valid_authorization_is_accepted():
    validate_recovery_authorization(
        auth(), subject="instance-1", evidence_digest="evidence-1",
        now="2026-09-25T12:00:00Z",
    )


@pytest.mark.parametrize(
    ("authorization", "subject", "evidence", "now", "message"),
    [
        (None, "instance-1", "evidence-1", "2026-09-25T12:00:00Z", "required"),
        (auth(decision="deny"), "instance-1", "evidence-1", "2026-09-25T12:00:00Z", "denied"),
        (auth(), "other", "evidence-1", "2026-09-25T12:00:00Z", "subject mismatch"),
        (auth(), "instance-1", "other", "2026-09-25T12:00:00Z", "evidence mismatch"),
        (auth(expires_at="2026-09-25T12:00:00Z"), "instance-1", "evidence-1", "2026-09-25T12:00:00Z", "expired"),
    ],
)
def test_invalid_authorization_fails_closed(authorization, subject, evidence, now, message):
    with pytest.raises(AuthorizationError, match=message):
        validate_recovery_authorization(
            authorization, subject=subject, evidence_digest=evidence, now=now
        )


def test_authorization_is_immutable():
    authorization = auth()
    with pytest.raises(Exception):
        authorization.decision = "deny"


def test_authorization_digest_is_deterministic():
    assert auth().authorization_digest == auth().authorization_digest
