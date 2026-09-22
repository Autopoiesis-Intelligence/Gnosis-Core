import pytest

from gnosis.evolution.provenance import DiagnosticEvidence


def test_diagnostic_evidence_has_stable_digest_and_monotonic_lifecycle():
    e = DiagnosticEvidence(
        "e1", "case-1", "state-1", "candidate-1", "EPHEMERAL",
        {"metric": 1}, limitations=("causality-unspecified",),
    )
    assert e.evidence_digest
    observed = e.advance("OBSERVED")
    durable = observed.advance("REPRODUCED").advance("VERIFIED").advance("DURABLE")
    assert durable.lifecycle == "DURABLE"
    with pytest.raises(ValueError):
        durable.advance("OBSERVED")


def test_diagnostic_evidence_rejects_tampered_digest():
    with pytest.raises(ValueError):
        DiagnosticEvidence(
            "e1", "case-1", "state-1", "candidate-1", "OBSERVED",
            {"metric": 1}, evidence_digest="tampered",
        )


def test_diagnostic_evidence_is_distinct_from_evolution_memory():
    from gnosis.storage.evolution_memory import EvolutionMemoryRecord
    assert DiagnosticEvidence is not EvolutionMemoryRecord
