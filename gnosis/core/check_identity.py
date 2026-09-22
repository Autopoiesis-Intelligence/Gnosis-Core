"""Identity and provenance for individual verification checks."""
from __future__ import annotations
from dataclasses import dataclass
from gnosis.core.types import _stable_hash

@dataclass(frozen=True)
class CheckIdentity:
    obligation_id: str
    check_id: str
    check_digest: str

def check_identity(obligation_id: str, check_id: str, check_definition: object) -> CheckIdentity:
    return CheckIdentity(obligation_id, check_id, _stable_hash({
        "obligation_id": obligation_id,
        "check_id": check_id,
        "definition": check_definition,
    }))

def verify_check_identity(identity: CheckIdentity, check_definition: object) -> bool:
    expected=check_identity(identity.obligation_id,identity.check_id,check_definition)
    return expected == identity

def verify_check_execution(identity: CheckIdentity, executed_check_id: str, passed: bool) -> None:
    if executed_check_id != identity.check_id:
        raise ValueError("executed check identity mismatch")
    if not passed:
        raise ValueError("verification check failed")
