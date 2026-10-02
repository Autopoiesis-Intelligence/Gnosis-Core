import pytest

from gnosis.self_learning.admitted_learning_commit import commit_admitted_learning
from gnosis.self_learning.learning_evidence_admission import create_admission

def make_admission(**overrides):
    values = dict(
        source_contract_id="sha256:source",
        verification_refs=("commit:abc", "workflow:100", "job:200"),
        evidence_refs=("ci:sha256:evidence",),
        evidence_digest="sha256:evidence",
        privacy_classification="PUBLIC",
        learning_scope="first-task",
        status="ADMITTED",
    )
    values.update(overrides)
    return create_admission(**values)

def test_admitted_evidence_can_create_learning_commit():
    commit = commit_admitted_learning(
        admission=make_admission(),
        source_state="VERIFIED_CLOSED",
        closure_verified=True,
        closure_digest="sha256:closure",
        feedback_id="feedback-1",
        learning_class="LEARNING_SIGNAL",
    )
    assert commit.status == "PROPOSED"
    assert commit.evidence_refs == ("ci:sha256:evidence",)

@pytest.mark.parametrize(
    "overrides",
    [
        {"status": "PROPOSED"},
        {"privacy_classification": "PRIVATE"},
    ],
)
def test_non_admitted_learning_evidence_cannot_create_learning_commit(overrides):
    admission = make_admission(**overrides)
    with pytest.raises(PermissionError, match="not admitted"):
        commit_admitted_learning(
            admission=admission,
            source_state="VERIFIED_CLOSED",
            closure_verified=True,
            closure_digest="sha256:closure",
            feedback_id="feedback-1",
            learning_class="LEARNING_SIGNAL",
        )

def test_unverified_source_state_cannot_create_learning_commit():
    with pytest.raises(PermissionError, match="not admitted"):
        commit_admitted_learning(
            admission=make_admission(),
            source_state="OPEN",
            closure_verified=True,
            closure_digest="sha256:closure",
            feedback_id="feedback-1",
            learning_class="LEARNING_SIGNAL",
        )

def test_learning_commit_has_no_execution_authority():
    commit = commit_admitted_learning(
        admission=make_admission(),
        source_state="VERIFIED_CLOSED",
        closure_verified=True,
        closure_digest="sha256:closure",
        feedback_id="feedback-1",
        learning_class="COUNTEREXAMPLE",
    )
    from gnosis.self_learning.admitted_learning_commit import creates_execution_authority
    assert creates_execution_authority(commit=commit) is False
