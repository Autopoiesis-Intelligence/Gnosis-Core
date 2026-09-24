from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from gnosis.control.capabilities import Capabilities
from gnosis.domain.identity.types import Identity
from gnosis.domain.scope.types import Scope
from gnosis.domain.task_context.model import TaskContext

@dataclass(frozen=True)
class EvidenceReceipt:
    parent_hash: str
    payload_hash: str
    timestamp_ms: int
    signature: str | None = None

@dataclass(frozen=True)
class OperationEnvelope:
    envelope_id: str
    schema_version: str
    timestamp_ms: int
    identity: Identity
    task_context: TaskContext
    capabilities: Capabilities
    action: str
    payload: Any
    target_resource: str
    evidence: EvidenceReceipt
    