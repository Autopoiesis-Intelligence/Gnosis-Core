from __future__ import annotations

from gnosis.reflection.owner_authorization_context import (
    OwnerAuthorizationExecutionContext,
    verify_for_execution_context,
)

from tests.reflection.test_owner_authorization import Resolver, make_authorization
from gnosis.reflection.owner_authorization import TrustedIssuerKey
from nacl.signing import SigningKey
import pytest


def test_execution_context_requires_all_bindings() -> None:
    signing_key = SigningKey.generate()
    trusted = TrustedIssuerKey("owner-1", "v1", signing_key.verify_key.encode())
    authorization = make_authorization(signing_key)

    context = OwnerAuthorizationExecutionContext(
        now=150,
        authority_scope=frozenset({"execute"}),
        policy_version="policy-1",
        evolution_identity="evolution:1",
        parent_state_digest="parent:1",
        request_provenance="request:1",
    )

    assert verify_for_execution_context(authorization, Resolver(trusted), context) == trusted


def test_execution_context_binding_mismatch_fails_closed() -> None:
    signing_key = SigningKey.generate()
    trusted = TrustedIssuerKey("owner-1", "v1", signing_key.verify_key.encode())
    authorization = make_authorization(signing_key)

    context = OwnerAuthorizationExecutionContext(
        now=150,
        authority_scope=frozenset({"execute"}),
        policy_version="policy-2",
        evolution_identity="evolution:1",
        parent_state_digest="parent:1",
        request_provenance="request:1",
    )

    with pytest.raises(PermissionError, match="policy mismatch"):
        verify_for_execution_context(authorization, Resolver(trusted), context)
