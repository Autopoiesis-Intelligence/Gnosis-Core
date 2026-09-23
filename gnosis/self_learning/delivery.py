"""Partner specialized Core delivery package specification."""
from __future__ import annotations
import hashlib, json
from dataclasses import dataclass

@dataclass(frozen=True)
class DeliveryManifest:
    package_id: str
    core_id: str
    contract_refs: tuple[str, ...]
    knowledge_scope: str
    evidence_refs: tuple[str, ...]
    excluded_components: tuple[str, ...]
    revision: str
    status: str = "PROPOSED"

def create_delivery_manifest(*, core_id: str, contract_refs: tuple[str,...], knowledge_scope: str, evidence_refs: tuple[str,...], excluded_components: tuple[str,...], revision: str) -> DeliveryManifest:
    if not core_id.strip() or not knowledge_scope.strip() or not revision.strip():
        raise ValueError("delivery identity fields are required")
    if not contract_refs or not evidence_refs or not excluded_components:
        raise ValueError("delivery manifest must declare contracts, evidence and exclusions")
    canonical={"core_id":core_id,"contract_refs":contract_refs,"knowledge_scope":knowledge_scope,"evidence_refs":evidence_refs,"excluded_components":excluded_components,"revision":revision}
    pid="sha256:"+hashlib.sha256(json.dumps(canonical,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return DeliveryManifest(pid,core_id,contract_refs,knowledge_scope,evidence_refs,excluded_components,revision)

def authorize_delivery(manifest: DeliveryManifest, *, allowed_scopes: set[str]) -> DeliveryManifest:
    canonical={"core_id":manifest.core_id,"contract_refs":manifest.contract_refs,"knowledge_scope":manifest.knowledge_scope,"evidence_refs":manifest.evidence_refs,"excluded_components":manifest.excluded_components,"revision":manifest.revision}
    expected="sha256:"+hashlib.sha256(json.dumps(canonical,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    if manifest.package_id != expected:
        raise ValueError("delivery manifest identity does not match immutable fields")
    if manifest.knowledge_scope not in allowed_scopes:
        raise PermissionError("delivery scope is not authorized")
    return manifest


def validate_delivery_build_binding(manifest: DeliveryManifest, *, expected_core_id: str) -> DeliveryManifest:
    authorize_delivery(manifest, allowed_scopes={manifest.knowledge_scope})
    if manifest.core_id != expected_core_id:
        raise PermissionError("delivery core identity mismatch")
    return manifest


def validate_delivery_build_binding(manifest: DeliveryManifest, *, expected_core_id: str) -> DeliveryManifest:
    authorize_delivery(manifest, allowed_scopes={manifest.knowledge_scope})
    if manifest.core_id != expected_core_id:
        raise PermissionError("delivery core identity mismatch")
    return manifest
