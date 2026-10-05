"""Canonical identity for the execution policy bound to owner authorization."""
from __future__ import annotations

from dataclasses import dataclass

from gnosis.evolution.provenance import canonical_digest


@dataclass(frozen=True)
class PolicyIdentity:
    """Immutable identity of one exact execution-policy context."""

    policy_version: str
    policy_binding_digest: str

    @classmethod
    def from_material(cls, *, policy_version: str, execution_scope: str) -> "PolicyIdentity":
        if not isinstance(policy_version, str) or not policy_version.strip():
            raise ValueError("policy version is required")
        if not isinstance(execution_scope, str) or not execution_scope.strip():
            raise ValueError("execution scope is required")
        digest = canonical_digest(
            {
                "policy_version": policy_version,
                "execution_scope": execution_scope,
            }
        )
        return cls(
            policy_version=policy_version,
            policy_binding_digest=digest,
        )

    def is_valid(self) -> bool:
        return bool(
            self.policy_version
            and self.policy_binding_digest
        )
