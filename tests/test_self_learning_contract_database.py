from pathlib import Path
import json

from gnosis.self_learning.contract_database import build_contract_database, write_contract_database


def _contract(root: Path, cid: str, title: str, status: str = "DESIGNED / NOT_IMPLEMENTED", refs: str = "") -> None:
    path = root / "docs" / "architecture" / f"{cid}_CONTRACT.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"# {cid} — {title}\n\n## Status\n\n{status}\n\n{refs}\n",
        encoding="utf-8",
    )


def _registry(root: Path, rows: str) -> None:
    path = root / "docs" / "partners" / "PARTNER_CONTRACT_REGISTRY.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "# Partner Contract Registry\n\n| CONTRACT-ID | Status | Source |\n|---|---|---|\n"
        + rows,
        encoding="utf-8",
    )


def test_build_database_is_deterministic_and_tracks_dependencies(tmp_path: Path):
    _contract(tmp_path, "E7.01", "A")
    _contract(tmp_path, "E7.02", "B", refs="Depends on E7.01.")
    _registry(tmp_path, "| E7.01 | DESIGNED / NOT_IMPLEMENTED | A |\n| E7.02 | DESIGNED / NOT_IMPLEMENTED | B |\n")

    first = build_contract_database(tmp_path)
    second = build_contract_database(tmp_path)

    assert first.as_dict() == second.as_dict()
    assert [c.contract_id for c in first.contracts] == ["E7.01", "E7.02"]
    assert first.contracts[1].dependencies == ("E7.01",)
    assert first.findings == ()


def test_build_database_detects_registry_drift_and_missing_dependency(tmp_path: Path):
    _contract(tmp_path, "E7.01", "A", status="IMPLEMENTED / UNVERIFIED")
    _contract(tmp_path, "E7.02", "B", refs="Depends on E7.99.")
    _registry(tmp_path, "| E7.01 | DESIGNED / NOT_IMPLEMENTED | A |\n| E7.03 | DESIGNED / NOT_IMPLEMENTED | C |\n")

    db = build_contract_database(tmp_path)

    assert "STATUS_DRIFT:E7.01:registry=DESIGNED / NOT_IMPLEMENTED:artifact=IMPLEMENTED / UNVERIFIED" in db.findings
    assert "ARTIFACT_MISSING:E7.03" in db.findings
    assert "DEPENDENCY_MISSING:E7.02->E7.99" in db.findings


def test_write_database_is_atomic_and_logs_generation(tmp_path: Path):
    _contract(tmp_path, "E7.01", "A")
    _registry(tmp_path, "| E7.01 | DESIGNED / NOT_IMPLEMENTED | A |\n")
    db = build_contract_database(tmp_path)

    output, log = write_contract_database(db, tmp_path, source_revision="test-revision")
    payload = json.loads(output.read_text(encoding="utf-8"))
    event = json.loads(log.read_text(encoding="utf-8").splitlines()[-1])

    assert payload["authority"] == "index_only"
    assert payload["source_revision"] == "test-revision"
    assert payload["contracts"][0]["source_digest"].startswith("sha256:")
    assert event["event"] == "contract_database.generated"
    assert event["source_revision"] == "test-revision"
