"""Canonical Core gap domain and detector.

Only hypothesis derivation lives here; no mutation, authorization, or
capability installation is performed by this module.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence
import hashlib, json

@dataclass(frozen=True)
class GapHypothesis:
    gap_id: str
    source_records: tuple[str, ...]
    trigger_kind: str
    description: str
    conditions: tuple[str, ...] = ()
    counterevidence: tuple[str, ...] = ()
    status: str = "HYPOTHESIS"
    provenance: str = "core-gap-detector"

def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()

class GapDetector:
    def detect(self, *, history: Sequence[Mapping[str, Any]], evidence: Sequence[Mapping[str, Any]]=(), tensions: Sequence[Mapping[str, Any]]=(), forecast_errors: Sequence[Mapping[str, Any]]=(), minimum_repetitions: int=2) -> tuple[GapHypothesis,...]:
        if minimum_repetitions < 2: raise ValueError("minimum_repetitions must be >= 2")
        records=tuple(history)+tuple(evidence)+tuple(tensions)+tuple(forecast_errors)
        groups={}
        for i,r in enumerate(records):
            kind=str(r.get("kind",r.get("type","unknown"))); status=str(r.get("status",r.get("outcome",""))).upper()
            reason=str(r.get("reason",r.get("pattern",r.get("error","")))).strip()
            unresolved=status in {"FAILED","REJECTED","REGRESSION","UNRESOLVED","INCONCLUSIVE","ERROR"} or bool(r.get("unresolved",False))
            if not reason or not unresolved: continue
            groups.setdefault((kind,reason),[]).append((str(r.get("record_id",f"record:{i}")),r))
        out=[]
        for (kind,reason),items in sorted(groups.items()):
            if len(items)<minimum_repetitions: continue
            refs=tuple(x[0] for x in items)
            out.append(GapHypothesis("gap:"+_digest({"kind":kind,"reason":reason,"source_records":refs})[:24],refs,kind,f"Repeated unresolved pattern: {reason}",(f"pattern_kind={kind}",f"minimum_repetitions={minimum_repetitions}"),tuple(str(x.get("counterevidence")) for _,x in items if x.get("counterevidence"))))
        return tuple(out)
