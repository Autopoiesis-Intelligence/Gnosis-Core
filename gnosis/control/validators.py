from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, is_dataclass
from typing import Any

from gnosis.control.capabilities import ALLOWED_CAPABILITIES, CapabilityToken
from gnosis.control.envelope import OperationEnvelope
from gnosis.domain.identity.types import Identity
from gnosis.domain.scope.types import Scope
from gnosis.domain.task_context.model import TaskContext

def _canonical_bytes(value: Any) -> bytes:
    if is_dataclass(value):
        value = asdict(value)
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

def sha256_payload(payload: Any) -> str:
    return hashlib.sha256(_canonical_bytes(payload)).hexdigest()

def validate_identity(identity: Identity, now_ms: int) -> str | None:
    if not identity.actor_id or not identity.tenant_id or not identity.issuer:
        return "INVALID_IDENTITY"
    if identity.issued_at_ms > identity.expires_at_ms:
        return "INVALID_IDENTITY_WINDOW"
    if now_ms < identity.issued_at_ms or now_ms >= identity.expires_at_ms:
        return "IDENTITY_EXPIRED"
    return None

def validate_scope(scope: Scope, identity: Identity, now_ms: int) -> str | None:
    if not scope.scope_id or not scope.tenant_id:
        return "INVALID_SCOPE"
    if scope.tenant_id != identity.tenant_id:
        return "TENANT_MISMATCH"
    if now_ms >= scope.valid_until_ms:
        return "SCOPE_EXPIRED"
    if any(not resource for resource in scope.allowed_resources):
        return "INVALID_SCOPE"
    return None

def validate_task_context(context: TaskContext, identity: Identity, scope: Scope) -> str | None:
    if not context.task_id or not context.root_task_id or not context.deterministic_seed:
        return "INVALID_TASK_CONTEXT"
    if context.tenant_id != identity.tenant_id or context.actor_id != identity.actor_id:
        return "TENANT_MISMATCH"
    if context.scope_id != scope.scope_id:
        return "SCOPE_MISMATCH"
    budget = context.budget
    if budget.current_iteration < 0 or budget.max_iterations < 0 or budget.current_iteration > budget.max_iterations:
        return "BUDGET_EXCEEDED"
    if budget.tokens_consumed < 0 or budget.token_limit < 0 or budget.tokens_consumed > budget.token_limit:
        return "BUDGET_EXCEEDED"
    if budget.max_depth < 0:
        return "INVALID_BUDGET"
    return None

def validate_envelope(envelope: OperationEnvelope, now_ms: int) -> str | None:
    if envelope.schema_version != "2.0.0":
        return "UNSUPPORTED_SCHEMA_VERSION"
    if not envelope.envelope_id or not envelope.action or not envelope.target_resource:
        return "INVALID_ENVELOPE"
    identity_error = validate_identity(envelope.identity, now_ms)
    if identity_error:
        return identity_error
    expected = sha256_payload(envelope.payload)
    if envelope.evidence.payload_hash != expected:
        return "INVALID_EVIDENCE_HASH"
    return None

def authorize_operation(envelope: OperationEnvelope, required_capability: CapabilityToken, now_ms: int) -> str | None:
    identity_error = validate_identity(envelope.identity, now_ms)
    if identity_error:
        return identity_error
    if required_capability not in ALLOWED_CAPABILITIES:
        return "UNKNOWN_CAPABILITY"
    if required_capability not in envelope.capabilities.granted_capabilities:
        return "UNAUTHORIZED_CAPABILITY"
    if envelope.identity.tenant_id != envelope.task_context.tenant_id:
        return "TENANT_MISMATCH"
    if envelope.task_context.scope_id == "":
        return "INVALID_SCOPE"
    return None
