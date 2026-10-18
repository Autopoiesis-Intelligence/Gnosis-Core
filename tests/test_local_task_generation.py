import pytest

from gnosis.task_generation import TaskGenerationError, generate_task_candidate


@pytest.fixture
def finding():
    return {
        "finding_id": "F-001",
        "title": "Reflection persistence lacks end-to-end evidence",
        "observation": "The persistence path is documented but not verified on current main.",
        "recommended_action": "Add reproducible end-to-end tests for reflection persistence.",
        "acceptance_criteria": [
            "A real test persists and reloads a reflection report.",
            "The test fails when persistence is disabled.",
        ],
        "evidence_required": [
            "pytest result tied to exact commit",
            "reopen/reload assertion",
        ],
        "source_refs": [
            "docs/CORE_REFLECTION_R1_TASK.md",
            "STATUS.md",
        ],
    }


def test_generation_is_deterministic_and_provenance_bound(finding):
    kwargs = {
        "source_revision": "abc123",
        "allowed_scope": ["tests/test_reflection_persistence.py"],
        "forbidden_scope": ["gnosis/core/*", "gnosis/memory/*"],
    }
    first = generate_task_candidate(finding, **kwargs)
    second = generate_task_candidate(finding, **kwargs)

    assert first == second
    assert first["task_id"].startswith("task-")
    assert first["source_finding"]["source_revision"] == "abc123"
    assert first["provenance"]["identity_sha256"]


def test_candidate_has_no_execution_or_verification_authority(finding):
    candidate = generate_task_candidate(
        finding,
        source_revision="abc123",
        allowed_scope=["tests/*"],
        forbidden_scope=["gnosis/core/*"],
    )

    assert candidate["status"] == "PROPOSED"
    assert candidate["authority"] == {
        "may_execute": False,
        "may_modify_core": False,
        "may_mark_verified": False,
        "requires_independent_validation": True,
    }
    assert candidate["implementation_state"] == "NOT_STARTED"
    assert candidate["verification_state"] == "NOT_VERIFIED"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("finding_id", ""),
        ("recommended_action", None),
        ("acceptance_criteria", []),
        ("evidence_required", [""]),
        ("source_refs", []),
    ],
)
def test_incomplete_source_is_rejected(finding, field, value):
    finding[field] = value
    with pytest.raises(TaskGenerationError):
        generate_task_candidate(
            finding,
            source_revision="abc123",
            allowed_scope=["tests/*"],
            forbidden_scope=["gnosis/core/*"],
        )


def test_overlapping_scope_is_rejected(finding):
    with pytest.raises(TaskGenerationError, match="must not overlap"):
        generate_task_candidate(
            finding,
            source_revision="abc123",
            allowed_scope=["tests/*"],
            forbidden_scope=["tests/*"],
        )


def test_changed_source_revision_changes_identity(finding):
    first = generate_task_candidate(
        finding,
        source_revision="abc123",
        allowed_scope=["tests/*"],
        forbidden_scope=["gnosis/core/*"],
    )
    second = generate_task_candidate(
        finding,
        source_revision="def456",
        allowed_scope=["tests/*"],
        forbidden_scope=["gnosis/core/*"],
    )

    assert first["task_id"] != second["task_id"]
