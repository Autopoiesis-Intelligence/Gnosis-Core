"""Targeted E7.59-A authority-provenance boundary experiment."""
from __future__ import annotations

import copy

import pytest

from gnosis.reflection.authority import (
    ExecutionAuthorization,
    ExecutionCommitRequest,
    ExecutionIntentSnapshot,
)
from gnosis.reflection.authorization_validity import AuthorizationValidity


def test_authorization_validity_has_no_issuer_provenance():
    validity = AuthorizationValidity(
        authorization_id="forged-authorization",
        policy_version="policy-v1",
        validity_evidence_digest="evidence-digest",
    )

    # The current validity contract authenticates fields but has no issuer field.
    assert not hasattr(validity, "issuer_id")
    assert not hasattr(validity, "authority_root")


def test_execution_authorization_can_be_constructed_without_issuer():
    auth = ExecutionAuthorization(
        request_provenance="test-provenance",
        owner_approved=True,
        evolution_identity="test-evolution",
        approval_id="forged-approval",
    )

    # This is the exact static boundary we need runtime protection against.
    assert auth.can_execute is True


def test_untrusted_authorization_is_not_equivalent_to_trusted_issuance():
    validity = AuthorizationValidity(
        authorization_id="forged-approval",
        policy_version="policy-v1",
        validity_evidence_digest="evidence-digest",
    )
    auth = ExecutionAuthorization(
        request_provenance="test-provenance",
        owner_approved=True,
        evolution_identity="test-evolution",
        approval_id=validity.authorization_id,
    )

    # Current model accepts the constructed authorization as executable.
    # This test intentionally records the authority gap; it must NOT be
    # promoted to CI_PROVEN evidence of actual Core mutation.
    assert auth.can_execute is True
    assert auth.approval_id == validity.authorization_id
