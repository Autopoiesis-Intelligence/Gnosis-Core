""""Build a compact, deterministic, read-only project context snapshot.

Claims are deliberately separated from their source references and evidence status.
This module does not initialize databases, mutate repository state, or grant authority.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import re
import subprocess
from typing import Any


@dataclass(frozen=True)
class ContextSnapshot:
    schema_version: int
    repository: dict[str, Any]
    branch: dict[str, Any]
    head: dict[str, Any]
    active_phase: dict[str, Any]
    active_task: dict[str, Any]
    implementation_state: dict[str, Any]
    verification_state: dict[str, Any]
    acceptance_state: dict[str, Any]
    next_permitted_action: dict[str, Any]
    open_findings: dict[str, Any]
    missing_sources: list[str]
    source_documents: dict[str, str] | None = None

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        if result["source_documents"] is None:
            result.pop("source_documents")
        return result


def _git(root: Path, *args: str) -> str:
    try:
        return subprocess.check_output(
            ["git", *args], cwd=root, text=True, stderr=subprocess.DEVNULL
        ).strip() or "UNKNOWN"
    except (OSError, subprocess.CalledProcessError):
        return "UNKNOWN"


def _read(root: Path, relative: str) -> str | None:
    path = root / relative
    if not path.is_file():
        return None
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return None


def _claim(value: str, status: str, source: str | None = None, **extra: Any) -> dict[str, Any]:
    claim: dict[str, Any] = {"value": value, "status": status}
    if source:
        claim["source"] = source
    claim.update(extra)
    return claim


def _repository_slug(remote: str) -> str:
    if remote == "UNKNOWN":
        return "UNKNOWN"
    value = remote.strip().removesuffix(".git").rstrip("/")
    if value.startswith("git@github.com:"):
        value = value.removeprefix("git@github.com:")
    elif value.startswith("https://github.com/"):
        value = value.removeprefix("https://github.com/")
    elif value.startswith("http://github.com/"):
        value = value.removeprefix("http://github.com/")
    return value if "/" in value else "UNKNOWN"


def _phase(ledger: str | None) -> dict[str, Any]:
    if not ledger:
        return _claim("UNKNOWN", "UNKNOWN", "docs/PHASE_LEDGER.md#current-phase")
    section = re.search(
        r"^##\s+Current phase\s*$([\s\S]*?)(?=^##\s|\Z)",
        ledger,
        re.MULTILINE | re.IGNORECASE,
    )
    if not section:
        return _claim("UNKNOWN", "UNKNOWN", "docs/PHASE_LEDGER.md#current-phase")
    heading = re.search(r"^###\s+(.+?)\s*$", section.group(1), re.MULTILINE)
    if not heading:
        return _claim("UNKNOWN", "UNKNOWN", "docs/PHASE_LEDGER.md#current-phase")
    return _claim(heading.group(1).strip(), "OBSERVED", "docs/PHASE_LEDGER.md#current-phase")


def _document_repository_values(documents: dict[str, str | None]) -> list[dict[str, str]]:
    values: list[dict[str, str]] = []
    pattern = re.compile(r"^\s*(?:[-*]\s*)?Repository:\s*([^\s]+)", re.MULTILINE | re.IGNORECASE)
    for path, content in documents.items():
        if not content:
            continue
        for match in pattern.finditer(content):
            value = match.group(1).strip().rstrip(".,;")
            if "/" in value:
                values.append({"value": value, "source": path})
    return values


def build_context_snapshot(
    root: str | Path = ".", *, include_source_documents: bool = False
) -> dict[str, Any]:
    """Return compact project context without changing files or repository state."""
    root = Path(root).resolve()
    paths = ("docs/PHASE_LEDGER.md", "AI_CONTEXT.md", "STATUS.md")
    documents = {path: _read(root, path) for path in paths}
    missing = [path for path, content in documents.items() if content is None]

    remote = _git(root, "config", "--get", "remote.origin.url")
    remote_slug = _repository_slug(remote)
    repo_values = _document_repository_values(documents)
    distinct_document_repos = {item["value"] for item in repo_values}
    repo_sources = list(repo_values)
    if remote_slug != "UNKNOWN":
        repo_sources.insert(0, {"value": remote_slug, "source": "git:remote.origin.url"})
        conflicting = any(
            item["value"].casefold() != remote_slug.casefold() for item in repo_values
        )
        repository = (
            _claim("UNKNOWN", "CONFLICT", sources=repo_sources)
            if conflicting
            else _claim(remote_slug, "OBSERVED", "git:remote.origin.url")
        )
    elif len(distinct_document_repos) > 1:
        repository = _claim("UNKNOWN", "CONFLICT", sources=repo_sources)
    elif len(distinct_document_repos) == 1:
        repository = _claim(next(iter(distinct_document_repos)), "REPORTED", sources=repo_sources)
    else:
        repository = _claim("UNKNOWN", "UNKNOWN", sources=repo_sources)

    branch_value = _git(root, "branch", "--show-current")
    head_value = _git(root, "rev-parse", "HEAD")
    branch = (
        _claim(branch_value, "OBSERVED", "git:branch")
        if branch_value != "UNKNOWN"
        else _claim("UNKNOWN", "UNKNOWN", "git:branch")
    )
    if branch_value == "UNKNOWN" and head_value != "UNKNOWN":
        branch = _claim("DETACHED", "OBSERVED", "git:branch")
    head = (
        _claim(head_value, "OBSERVED", "git:rev-parse HEAD")
        if head_value != "UNKNOWN"
        else _claim("UNKNOWN", "UNKNOWN", "git:rev-parse HEAD")
    )

    phase = _phase(documents["docs/PHASE_LEDGER.md"])
    raw = {path: content if content is not None else "UNKNOWN" for path, content in documents.items()}
    result = ContextSnapshot(
        schema_version=1,
        repository=repository,
        branch=branch,
        head=head,
        active_phase=phase,
        active_task=_claim("UNKNOWN", "UNKNOWN", "no structured active-task source"),
        implementation_state=_claim("UNKNOWN", "UNKNOWN", "no structured implementation evidence"),
        verification_state=_claim("UNKNOWN", "UNKNOWN", "no exact-head runtime/CI evidence source"),
        acceptance_state=_claim("UNKNOWN", "UNKNOWN", "no explicit acceptance record"),
        next_permitted_action=_claim(
            "Inspect canonical task and exact-head evidence; do not infer missing state.",
            "REPORTED",
            "docs/PHASE_LEDGER.md#required-evidence",
        ),
        open_findings=_claim("UNKNOWN", "UNKNOWN", "no structured findings source"),
        missing_sources=missing,
        source_documents=raw if include_source_documents else None,
    ).to_dict()
    return result
"