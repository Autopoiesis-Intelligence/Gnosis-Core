from gnosis.evolution.directory_candidate import DirectoryUsage, build_duplicate_candidate


def test_duplicate_candidate_blocks_referenced_or_unprovenanced_files() -> None:
    result = build_duplicate_candidate(
        ["a", "b", "c"],
        "digest",
        {
            "b": DirectoryUsage("b", referenced=True, provenance_id="p1"),
            "c": DirectoryUsage("c", provenance_id="p2"),
        },
    )
    assert result.blocked == ("b",)
    assert result.removable == ("c",)
    assert "candidate only" in result.reason


def test_duplicate_candidate_never_treats_missing_provenance_as_safe() -> None:
    result = build_duplicate_candidate(
        ["a", "b"],
        "digest",
        {"b": DirectoryUsage("b")},
    )
    assert result.removable == ()
    assert result.blocked == ("b",)


def test_duplicate_candidate_rejects_single_file() -> None:
    try:
        build_duplicate_candidate(["a"], "digest", {})
    except ValueError:
        pass
    else:
        raise AssertionError("single-file candidate was accepted")
