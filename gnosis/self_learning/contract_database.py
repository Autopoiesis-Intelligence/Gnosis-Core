"""Deterministic contract knowledge database for the Self-Learning layer.

This module indexes contract artifacts and the partner registry without granting
authority. It is deliberately outside gnosis.core and uses only the standard library.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

_HEADING = re.compile(r"^#\s+(E\d+(?:\.\d+)?)\s+[—-]\s+(.+?)\s*$", re.MULTILINE)
_STATUS = re.compile(r"^##\s+Status\s*\n+([^\n]+)", re.MULTILINE)
_REF = re.compile(r"\bE\d+(?:\.\d+)+\b")
_REGISTRY_ROW = re.compile(r"^\|\s*(E\d+(?:\.\d+)?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*$")


@dataclass(frozen=True)
class ContractRecord:
    contract_id: str
    title: str
    status: str
    source_path: str
    source_digest: str
    dependencies: tuple[str, ...]
    provenance: str = "self-learning-contract-database"


@dataclass(frozen=True)
class ContractDatabase:
    schema_version: str
    contract_scope: str
    contracts: tuple[ContractRecord, ...]
    registry_entries: tuple[tuple[str, str], ...]
    findings: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "contract_scope": self.contract_scope,
            "contracts": [asdict(item) for item in self.contracts],
            "registry_entries": [
                {"contract_id": cid, "status": status}
                for cid, status in self.registry_entries
            ],
            "findings": list(self.findings),
            "authority": "index_only",
            "provenance": "self-learning-contract-database",
        }


def _digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _parse_contract(path: Path, root: Path) -> ContractRecord | None:
    text = path.read_text(encoding="utf-8")
    heading = _HEADING.search(text)
    if heading is None:
        return None
    contract_id, title = heading.group(1), heading.group(2).strip()
    status_match = _STATUS.search(text)
    status = status_match.group(1).strip() if status_match else "UNKNOWN"
    refs = sorted(set(_REF.findall(text)) - {contract_id})
    return ContractRecord(
        contract_id=contract_id,
        title=title,
        status=status,
        source_path=path.relative_to(root).as_posix(),
        source_digest=f"sha256:{_digest(text)}",
        dependencies=tuple(refs),
    )


def _registry_entries(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    entries: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = _REGISTRY_ROW.match(line)
        if match:
            entries[match.group(1)] = match.group(2).strip()
    return entries


def build_contract_database(
    root: str | Path,
    *,
    scope_prefix: str = "E7.",
    registry_path: str = "docs/partners/PARTNER_CONTRACT_REGISTRY.md",
) -> ContractDatabase:
    """Build a deterministic, non-authoritative contract knowledge index."""
    root_path = Path(root).resolve()
    records: list[ContractRecord] = []
    for path in sorted((root_path / "docs").rglob("*CONTRACT.md")):
        record = _parse_contract(path, root_path)
        if record is not None and record.contract_id.startswith(scope_prefix):
            records.append(record)

    records.sort(key=lambda item: item.contract_id)
    artifacts = {item.contract_id for item in records}
    registry = _registry_entries(root_path / registry_path)

    findings: set[str] = set()
    for contract_id in sorted(artifacts - registry.keys()):
        findings.add(f"REGISTRY_MISSING:{contract_id}")
    for contract_id in sorted(registry.keys() - artifacts):
        if contract_id.startswith(scope_prefix):
            findings.add(f"ARTIFACT_MISSING:{contract_id}")
    for item in records:
        registry_status = registry.get(item.contract_id)
        if registry_status is not None and registry_status != item.status:
            findings.add(
                f"STATUS_DRIFT:{item.contract_id}:registry={registry_status}:artifact={item.status}"
            )
        for dependency in item.dependencies:
            if dependency.startswith(scope_prefix) and dependency not in artifacts:
                findings.add(f"DEPENDENCY_MISSING:{item.contract_id}->{dependency}")

    return ContractDatabase(
        schema_version="1",
        contract_scope=scope_prefix,
        contracts=tuple(records),
        registry_entries=tuple(sorted(registry.items())),
        findings=tuple(sorted(findings)),
    )


def write_contract_database(
    database: ContractDatabase,
    root: str | Path,
    *,
    output_path: str = "logs/contracts/partner_contract_database.json",
    log_path: str = "logs/contracts/partner_contract_database.jsonl",
    source_revision: str | None = None,
) -> tuple[Path, Path]:
    """Atomically write the current database and append one generation event."""
    root_path = Path(root).resolve()
    output = root_path / output_path
    log = root_path / log_path
    output.parent.mkdir(parents=True, exist_ok=True)

    payload = database.as_dict()
    payload["source_revision"] = source_revision
    serialized = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"

    temp = output.with_suffix(output.suffix + ".tmp")
    temp.write_text(serialized, encoding="utf-8")
    temp.replace(output)

    event = {
        "event": "contract_database.generated",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source_revision": source_revision,
        "database_digest": f"sha256:{_digest(serialized)}",
        "contract_count": len(database.contracts),
        "finding_count": len(database.findings),
        "output_path": output_path,
        "authority": "index_only",
    }
    with log.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")
    return output, log
