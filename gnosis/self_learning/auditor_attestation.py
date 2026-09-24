"""External auditor verification and attestation boundary (E7.86)."""
from __future__ import annotations
import hashlib,json
from dataclasses import dataclass
STATUSES={"PENDING","VERIFIED","REJECTED","DISPUTED","EXPIRED"}
@dataclass(frozen=True)
class AuditorAttestation:
    attestation_id:str; package_id:str; auditor_id:str; verified_digest:str; verification_scope:str; evidence_refs:tuple[str,...]; finding_refs:tuple[str,...]; status:str; attestation_revision:str
def create_attestation(*,package_id,auditor_id,verified_digest,verification_scope,evidence_refs,finding_refs, status="PENDING",attestation_revision="r1"):
    if status not in STATUSES: raise ValueError("invalid attestation status")
    if not all(x.strip() for x in (package_id,auditor_id,verified_digest,verification_scope,attestation_revision)): raise ValueError("attestation identity is required")
    if not evidence_refs: raise ValueError("verification evidence is required")
    c={"package_id":package_id,"auditor_id":auditor_id,"verified_digest":verified_digest,"verification_scope":verification_scope,"evidence_refs":evidence_refs,"finding_refs":finding_refs,"status":status,"attestation_revision":attestation_revision}
    aid="sha256:"+hashlib.sha256(json.dumps(c,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return AuditorAttestation(aid,package_id,auditor_id,verified_digest,verification_scope,evidence_refs,finding_refs,status,attestation_revision)
def attestation_is_valid(*,attestation,package_digest):
    return attestation.status=="VERIFIED" and attestation.verified_digest==package_digest and bool(attestation.evidence_refs)
def attestation_grants_authority(*,attestation): return False
