import pytest
from gnosis.core.lineage_runtime import LineageArtifact, LineageRuntime

def test_lineage_requires_same_cycle_and_parent():
    r=LineageRuntime(cycle_id="c1")
    g=LineageArtifact("DIAGNOSE","c1","gap:1")
    r=r.advance(g)
    i=LineageArtifact("INVESTIGATE","c1","inv:1","gap:1")
    r=r.advance(i)
    assert r.stage=="PROPOSE" and r.last_artifact_id=="inv:1"

def test_foreign_cycle_is_rejected():
    r=LineageRuntime(cycle_id="c1")
    with pytest.raises(ValueError): r.advance(LineageArtifact("DIAGNOSE","c2","gap:1"))

def test_wrong_parent_is_rejected():
    r=LineageRuntime(cycle_id="c1")
    r=r.advance(LineageArtifact("DIAGNOSE","c1","gap:1"))
    with pytest.raises(ValueError):
        r.advance(LineageArtifact("INVESTIGATE","c1","inv:1","gap:other"))

def test_missing_parent_on_later_stage_is_rejected():
    r=LineageRuntime(cycle_id="c1")
    r=r.advance(LineageArtifact("DIAGNOSE","c1","gap:1"))
    with pytest.raises(ValueError):
        r.advance(LineageArtifact("INVESTIGATE","c1","inv:1"))
