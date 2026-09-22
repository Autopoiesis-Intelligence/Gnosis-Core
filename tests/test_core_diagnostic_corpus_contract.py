from gnosis.core.diagnostic_corpus import DiagnosticCorpus

def test_core_diagnostic_corpus_detects_repeated_unresolved_pattern():
    corpus=DiagnosticCorpus()
    records=(
        {"record_id":"r1","kind":"test","status":"FAILED","reason":"same-gap"},
        {"record_id":"r2","kind":"test","status":"REGRESSION","reason":"same-gap"},
    )
    gaps=corpus.detect(history=records)
    assert len(gaps)==1
    assert gaps[0].source_records==("r1","r2")

def test_core_diagnostic_corpus_is_read_only_view():
    corpus=DiagnosticCorpus()
    assert not hasattr(corpus,"authorize")
    assert not hasattr(corpus,"commit")
