"""Contract tests for the read-only, compact context recovery CLI."""

import json
import subprocess
import sys
from pathlib import Path

from gnosis.context.snapshot import build_context_snapshot


def make_checkout(root: Path, *, git: bool = True) -> Path:
    (root / "docs").mkdir(parents=True)
    (root / "docs/PHASE_LEDGER.md").write_text(
        "# Phase Ledger\n\n## Current phase\n\n### MVP CONTEXT RECOVERY\n"
        "**Status:** IMPLEMENTATION\n",
        encoding="utf-8",
    )
    (root / "AI_CONTEXT.md").write_text(
        "# AI Context\n\nRepository: Autopoiesis-Intelligence/Gnosis-Core\n",
        encoding="utf-8",
    )
    (root / "STATUS.md").write_text(
        "# Status\n\nRepository: Autopoiesis-Intelligence/Gnosis-Core\n",
        encoding="utf-8",
    )
    if git:
        subprocess.run(["git", "init", "-q", str(root)], check=True)
        subprocess.run(
            ["git", "-C", str(root), "config", "user.email", "test@example.invalid"],
            check=True,
        )
        subprocess.run(
            ["git", "-C", str(root), "config", "user.name", "Test"],
            check=True,
        )
        subprocess.run(["git", "-C", str(root), "add", "."], check=True)
        subprocess.run(
            ["git", "-C", str(root), "commit", "-qm", "fixture"],
            check=True,
        )
    return root


def test_snapshot_is_compact_and_claims_have_source_references(tmp_path):
    root = make_checkout(tmp_path / "repo")
    snapshot = build_context_snapshot(root)

    assert snapshot["schema_version"] == 1
    assert snapshot["active_phase"]["value"] == "MVP CONTEXT RECOVERY"
    assert snapshot["active_phase"]["status"] == "OBSERVED"
    assert snapshot["active_phase"]["source"] == "docs/PHASE_LEDGER.md#current-phase"
    assert snapshot["active_task"]["status"] == "UNKNOWN"
    assert "source_documents" not in snapshot
    assert snapshot["head"] != "UNKNOWN"
    assert len(json.dumps(snapshot)) < 6000


def test_stale_repository_identity_is_reported_as_conflict(tmp_path):
    root = make_checkout(tmp_path / "repo")
    (root / "STATUS.md").write_text(
        "# Status\n\nRepository: legacy-owner/legacy-repository\n",
        encoding="utf-8",
    )

    snapshot = build_context_snapshot(root)

    assert snapshot["repository"]["status"] == "CONFLICT"
    assert len(snapshot["repository"]["sources"]) >= 2
    assert snapshot["repository"]["value"] == "UNKNOWN"


def test_missing_git_metadata_and_documents_are_explicit_unknowns(tmp_path):
    snapshot = build_context_snapshot(tmp_path / "empty")

    assert snapshot["head"]["status"] == "UNKNOWN"
    assert snapshot["branch"]["status"] == "UNKNOWN"
    assert snapshot["active_phase"]["status"] == "UNKNOWN"
    assert snapshot["active_task"]["status"] == "UNKNOWN"
    assert snapshot["missing_sources"]


def test_raw_documents_are_opt_in(tmp_path):
    root = make_checkout(tmp_path / "repo")
    snapshot = build_context_snapshot(root, include_source_documents=True)

    assert snapshot["source_documents"]["AI_CONTEXT.md"].startswith("# AI Context")


def test_cli_emits_valid_json_and_does_not_create_database(tmp_path):
    root = make_checkout(tmp_path / "repo")
    db = tmp_path / "context.db"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "gnosis.context.cli",
            "--root",
            str(root),
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    parsed = json.loads(result.stdout)
    assert parsed["schema_version"] == 1
    assert parsed["head"]["status"] == "OBSERVED"
    assert not db.exists()
    assert not list(root.glob("*.db"))


def test_cli_runs_against_real_repository_checkout():
    repository_root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "gnosis.context.cli",
            "--root",
            str(repository_root),
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    parsed = json.loads(result.stdout)
    assert parsed["schema_version"] == 1
    assert parsed["head"]["status"] == "OBSERVED"
    assert len(parsed["head"]["value"]) == 40
    assert "source_documents" not in parsed
