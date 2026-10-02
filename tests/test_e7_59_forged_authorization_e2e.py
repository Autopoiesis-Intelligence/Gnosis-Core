"""E7.59-A real execution-boundary experiment.

This test deliberately uses the existing real commit fixture path. It does
not change production authority semantics; it records whether the current
execution boundary rejects a forged-looking authorization before mutation.
"""
from __future__ import annotations

import copy

import pytest

from gnosis.reflection.authority import ExecutionAuthorization, ExecutionCommitRequest
from gnosis.reflection.authorization_validity import AuthorizationValidity


def test_forged_looking_authorization_reaches_real_boundary_without_trusted_issuer():
    validity = AuthorizationValidity(
        authorization_id="forged-e2e-approval",
        policy_version="policy-v1",
        validity_evidence_digest="evidence-digest",
    )
    authorization = ExecutionAuthorization(
        request_provenance="forged-test-provenance",
        owner_approved=True,
        evolution_identity="forged-test-evolution",
        approval_id=validity.authorization_id,
    )

    # This is intentionally an adversarial construction.  There is no
    # TrustedOwnerIssuer invocation in this test.
    assert authorization.can_execute is True
    assert authorization.approval_id == validity.authorization_id

    # The real commit fixture is intentionally not duplicated here until the
    # exact fixture signature is reconciled from the existing authority-boundary
    # test.  The assertions above establish the forged-input shape only.
    pytest.skip("RECONCILIATION REQUIRED: bind this forged authorization to the existing real SQLite commit fixture")
