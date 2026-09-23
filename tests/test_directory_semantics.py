from gnosis.evolution.directory_candidate import DirectoryUsage, build_duplicate_candidate
from gnosis.evolution.directory_semantics import verify_shadow_semantics


def _candidate():
    return build_duplicate_candidate(["a", "b"], "digest", {
        "b": DirectoryUsage("b", provenance_id="p1"),
    })


def test_shadow_semantics_preserves_non_required_duplicate() -> None:
    result = verify_shadow_semantics(
        _candidate(),
        {"b": DirectoryUsage("b", provenance_id="p1")},
        required_paths=["a"],
    )
    assert result.preserved
    assert result.removed_paths == ("b",)


def test_shadow_semantics_rejects_required_removal() -> None:
    result = verify_shadow_semantics(
        _candidate(),
        {"b": DirectoryUsage("b", provenance_id="p1")},
        required_paths=["b"],
    )
    assert not result.preserved
    assert result.removed_paths == ()


def test_shadow_semantics_rejects_referenced_removal() -> None:
    result = verify_shadow_semantics(
        _candidate(),
        {"b": DirectoryUsage("b", referenced=True, provenance_id="p1")},
    )
    assert not result.preserved
    assert result.removed_paths == ()
