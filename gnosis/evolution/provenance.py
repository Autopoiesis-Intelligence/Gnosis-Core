"""Tamper-evident provenance for bounded evolution evidence."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Mapping


def canonical_digest(value: Any) -> str:
    """Return a stable SHA-256 digest for JSON-compatible evidence."""
    payload = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass(frozen=True, init=False)
class EvidenceProvenance:
    execution_id: str
    candidate_id: str
    parent_state_id: str
    parent_state_digest: str
    proposed_state_digest: str
    evidence_digest: str
    evaluation_status: str
    shadow_status: str
    invariant_status: str
    governance_decision: str
    status: str
    proposed_state_content_id: str
    candidate_binding_digest: str
    _provenance_id_override: str
    _evolution_identity_override: str

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        fields = (
            "provenance_id", "execution_id", "candidate_id", "parent_state_id",
            "parent_state_digest", "proposed_state_digest", "evidence_digest",
            "evaluation_status", "shadow_status", "invariant_status",
            "governance_decision", "status", "evolution_identity",
            "proposed_state_content_id", "candidate_binding_digest",
        )
        if args:
            if len(args) == 15:
                values = dict(zip(fields, args))
            elif len(args) <= 13:
                legacy = (
                    "execution_id", "candidate_id", "parent_state_id", "parent_state_digest",
                    "proposed_state_digest", "evidence_digest", "evaluation_status",
                    "shadow_status", "invariant_status", "governance_decision", "status",
                    "proposed_state_content_id", "candidate_binding_digest",
                )
                values = dict(zip(legacy, args))
            else:
                raise TypeError("unsupported EvidenceProvenance positional arity")
        else:
            values = dict(kwargs)
        defaults = {"provenance_id":"","evolution_identity":"","status":"RECORDED",
                    "proposed_state_content_id":"","candidate_binding_digest":""}
        values = {**defaults, **values}
        required = (
            "execution_id","candidate_id","parent_state_id","parent_state_digest",
            "proposed_state_digest","evidence_digest","evaluation_status",
            "shadow_status","invariant_status","governance_decision",
        )
        for name in required:
            if name not in values:
                raise TypeError(f"missing required argument: {name}")
        object.__setattr__(self, "_provenance_id_override", values["provenance_id"])
        object.__setattr__(self, "_evolution_identity_override", values["evolution_identity"])
        for name in (
            "execution_id","candidate_id","parent_state_id","parent_state_digest",
            "proposed_state_digest","evidence_digest","evaluation_status",
            "shadow_status","invariant_status","governance_decision","status",
            "proposed_state_content_id","candidate_binding_digest",
        ):
            object.__setattr__(self, name, values[name])

    @property
    def evolution_identity(self) -> str:
        if self._evolution_identity_override:
            return self._evolution_identity_override
        return "evolution:" + canonical_digest({
            "candidate_id": self.candidate_id,
            "execution_id": self.execution_id,
            "parent_state_id": self.parent_state_id,
            "parent_state_digest": self.parent_state_digest,
            "proposed_state_digest": self.proposed_state_digest,
            "proposed_state_content_id": self.proposed_state_content_id,
            "candidate_binding_digest": self.candidate_binding_digest,
            "evidence_digest": self.evidence_digest,
            "evaluation_status": self.evaluation_status,
            "shadow_status": self.shadow_status,
            "invariant_status": self.invariant_status,
            "governance_decision": self.governance_decision,
            "provenance_id": self.provenance_id,
        })

    @property
    def provenance_id(self) -> str:
        if self._provenance_id_override:
            return self._provenance_id_override
        return "provenance:" + canonical_digest({
            "execution_id": self.execution_id,
            "candidate_id": self.candidate_id,
            "parent_state_id": self.parent_state_id,
            "parent_state_digest": self.parent_state_digest,
            "proposed_state_digest": self.proposed_state_digest,
            "proposed_state_content_id": self.proposed_state_content_id,
            "evidence_digest": self.evidence_digest,
            "evaluation_status": self.evaluation_status,
            "shadow_status": self.shadow_status,
            "invariant_status": self.invariant_status,
            "governance_decision": self.governance_decision,
        })[:24]


def execution_id(candidate_id: str, parent_state_id: str, evidence_digest: str, parent_state_digest: str = "", proposed_state_digest: str = "") -> str:
    if not candidate_id or not parent_state_id or not evidence_digest:
        raise ValueError("execution provenance requires candidate, parent state and evidence digest")
    return "execution:" + canonical_digest(
        {"candidate_id": candidate_id, "parent_state_id": parent_state_id, "parent_state_digest": parent_state_digest, "proposed_state_digest": proposed_state_digest, "evidence_digest": evidence_digest}
    )[:24]


def verify_evidence_digest(observations: Mapping[str, Any], expected_digest: str) -> bool:
    if not expected_digest:
        return False
    return canonical_digest(observations) == expected_digest


def build_provenance(
    *,
    candidate_id: str,
    parent_state_id: str,
    parent_state_digest: str,
    proposed_state_digest: str,
    observations: Mapping[str, Any],
    proposed_state_content_id: str = "",
    candidate_binding_digest: str = "",
    evidence_digest: str,
    evaluation_status: str,
    shadow_status: str,
    invariant_status: str,
    governance_decision: str,
) -> EvidenceProvenance:
    if not parent_state_digest or not proposed_state_digest:
        raise ValueError("state digests are required")
    # Empty binding is retained for legacy fixtures; canonical provenance must bind it before trusted activation.
    if not verify_evidence_digest(observations, evidence_digest):
        raise ValueError("evidence digest mismatch")
    return EvidenceProvenance(
        execution_id=execution_id(candidate_id, parent_state_id, evidence_digest, parent_state_digest, proposed_state_digest),
        candidate_id=candidate_id,
        parent_state_id=parent_state_id,
        parent_state_digest=parent_state_digest,
        proposed_state_digest=proposed_state_digest,
        evidence_digest=evidence_digest,
        proposed_state_content_id=proposed_state_content_id,
        candidate_binding_digest=candidate_binding_digest,
        evaluation_status=evaluation_status,
        shadow_status=shadow_status,
        invariant_status=invariant_status,
        governance_decision=governance_decision,
    )


@dataclass(frozen=True)
class ProvenanceCrossCheck:
    valid: bool
    reasons: tuple[str, ...]


def crosscheck_provenance(
    *,
    provenance: EvidenceProvenance,
    candidate_id: str,
    parent_state_id: str,
    parent_state_digest: str,
    proposed_state_digest: str,
    observations: Mapping[str, Any],
    evidence_digest: str,
    execution_id_value: str,
    evaluation_status: str,
    shadow_status: str,
    invariant_status: str,
    governance_decision: str,
    proposed_state_content_id: str = "",
    candidate_binding_digest: str = "",
) -> ProvenanceCrossCheck:
    """Verify every identity-bearing link before provenance can be trusted."""
    reasons: list[str] = []
    if provenance.candidate_id != candidate_id:
        reasons.append("candidate_id mismatch")
    if provenance.parent_state_id != parent_state_id:
        reasons.append("parent_state_id mismatch")
    if provenance.parent_state_digest != parent_state_digest:
        reasons.append("parent_state_digest mismatch")
    if provenance.proposed_state_digest != proposed_state_digest:
        reasons.append("proposed_state_digest mismatch")
    if provenance.proposed_state_content_id != proposed_state_content_id:
        reasons.append("proposed_state_content_id mismatch")
    if provenance.candidate_binding_digest != candidate_binding_digest:
        reasons.append("candidate_binding_digest mismatch")
    if provenance.evidence_digest != evidence_digest:
        reasons.append("evidence_digest mismatch")
    if provenance.execution_id != execution_id_value:
        reasons.append("execution_id mismatch")
    if provenance.evaluation_status != evaluation_status:
        reasons.append("evaluation_status mismatch")
    if provenance.shadow_status != shadow_status:
        reasons.append("shadow_status mismatch")
    if provenance.invariant_status != invariant_status:
        reasons.append("invariant_status mismatch")
    if provenance.governance_decision != governance_decision:
        reasons.append("governance_decision mismatch")
    if not verify_evidence_digest(observations, evidence_digest):
        reasons.append("observation digest mismatch")
    expected_execution = execution_id(candidate_id, parent_state_id, evidence_digest, parent_state_digest, proposed_state_digest)
    if execution_id_value != expected_execution:
        reasons.append("execution identity mismatch")
    expected_provenance = EvidenceProvenance(
        execution_id=execution_id_value,
        candidate_id=candidate_id,
        parent_state_id=parent_state_id,
        parent_state_digest=parent_state_digest,
        proposed_state_digest=proposed_state_digest,
        evidence_digest=evidence_digest,
        evaluation_status=evaluation_status,
        shadow_status=shadow_status,
        invariant_status=invariant_status,
        governance_decision=governance_decision,
        status=provenance.status,
        proposed_state_content_id=proposed_state_content_id,
        candidate_binding_digest=candidate_binding_digest,
    )
    if provenance.provenance_id != expected_provenance.provenance_id:
        reasons.append("provenance identity mismatch")
    return ProvenanceCrossCheck(valid=not reasons, reasons=tuple(reasons))


"""Immutable evidence produced by the in-Core diagnostic subsystem.

DiagnosticEvidence is intentionally distinct from EvolutionMemoryRecord:
memory records describe durable evolutionary history, while this object
describes a bounded diagnostic observation and its verification lifecycle.
"""

from dataclasses import dataclass
from typing import Mapping

from .provenance import canonical_digest


_ALLOWED = {"EPHEMERAL", "OBSERVED", "REPRODUCED", "VERIFIED", "DURABLE"}


@dataclass(frozen=True)
class DiagnosticEvidence:
    evidence_id: str
    case_id: str
    state_id: str
    candidate_id: str
    lifecycle: str
    observations: Mapping[str, object]
    provenance_refs: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()
    evidence_digest: str = ""

    def __post_init__(self) -> None:
        if not self.evidence_id.strip() or not self.case_id.strip():
            raise ValueError("diagnostic evidence identifiers must be non-empty")
        if self.lifecycle not in _ALLOWED:
            raise ValueError(f"unsupported diagnostic lifecycle: {self.lifecycle}")
        expected = canonical_digest(
            {
                "evidence_id": self.evidence_id,
                "case_id": self.case_id,
                "state_id": self.state_id,
                "candidate_id": self.candidate_id,
                "lifecycle": self.lifecycle,
                "observations": dict(self.observations),
                "provenance_refs": self.provenance_refs,
                "limitations": self.limitations,
            }
        )
        if self.evidence_digest and self.evidence_digest != expected:
            raise ValueError("diagnostic evidence digest mismatch")
        if not self.evidence_digest:
            object.__setattr__(self, "evidence_digest", expected)

    def advance(self, lifecycle: str, *, provenance_refs: tuple[str, ...] | None = None) -> "DiagnosticEvidence":
        order = ("EPHEMERAL", "OBSERVED", "REPRODUCED", "VERIFIED", "DURABLE")
        if lifecycle not in _ALLOWED or order.index(lifecycle) < order.index(self.lifecycle):
            raise ValueError("diagnostic lifecycle cannot move backwards")
        return DiagnosticEvidence(
            self.evidence_id, self.case_id, self.state_id, self.candidate_id,
            lifecycle, self.observations,
            self.provenance_refs if provenance_refs is None else provenance_refs,
            self.limitations,
        )
