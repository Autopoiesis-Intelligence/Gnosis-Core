"""Canonical rule identity for verification provenance."""
from __future__ import annotations
from dataclasses import dataclass
from gnosis.core.types import _stable_hash

@dataclass(frozen=True)
class RuleIdentity:
    rule_id: str
    rule_digest: str

def rule_identity(rule_id: str, rule_content: object) -> RuleIdentity:
    return RuleIdentity(rule_id, _stable_hash({"rule_id": rule_id, "content": rule_content}))

def verify_rule_identity(identity: RuleIdentity, rule_content: object) -> bool:
    return identity.rule_digest == rule_identity(identity.rule_id, rule_content).rule_digest
