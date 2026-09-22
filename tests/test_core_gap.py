from gnosis.core.gap import GapDetector

def test_core_gap_detector_only_emits_hypotheses():
    gaps=GapDetector().detect(history=({"kind":"transition","status":"FAILED","reason":"x","record_id":"1"},{"kind":"transition","status":"FAILED","reason":"x","record_id":"2"}))
    assert len(gaps)==1
    assert gaps[0].status=="HYPOTHESIS"
    assert gaps[0].provenance=="core-gap-detector"
