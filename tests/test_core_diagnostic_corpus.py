import pytest

from gnosis.core import Candidate, State
from gnosis.evolution.diagnostic_corpus import CoreDiagnosticCase, CoreDiagnosticCorpus
from gnosis.evolution.sandbox import SandboxBudget


def _candidate():
    state = State(elements={"x": 1})
    return state, Candidate(state.state_id, state.with_elements({"x": 2}), "diagnostic")


def observe(state, candidate):
    return {"parent": state.state_id, "candidate": candidate.candidate_id}


def test_core_diagnostic_corpus_is_bounded_and_sandboxed():
    state, candidate = _candidate()
    corpus = CoreDiagnosticCorpus((
        CoreDiagnosticCase("case-1", "bounded observation", observe, SandboxBudget(timeout_seconds=1.0)),
    ))
    result = corpus.run("case-1", state, candidate)
    assert result.accepted_for_evaluation is True
    assert result.execution.status == "COMPLETED"


def test_core_diagnostic_corpus_rejects_duplicate_case_ids():
    with pytest.raises(ValueError):
        CoreDiagnosticCorpus((
            CoreDiagnosticCase("same", "a", observe),
            CoreDiagnosticCase("same", "b", observe),
        ))
