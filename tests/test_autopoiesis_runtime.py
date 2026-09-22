import pytest
from gnosis.core.autopoiesis_runtime import AutopoiesisRuntime

def test_runtime_requires_sequential_stages():
    r=AutopoiesisRuntime(cycle_id="c1")
    for stage in ("DIAGNOSE","INVESTIGATE","PROPOSE","SHADOW","GOVERN","COMMIT"):
        r.require_stage(stage)
        r=r.advance(stage)
    assert r.stage=="DONE"

def test_runtime_rejects_stage_skip():
    r=AutopoiesisRuntime(cycle_id="c1")
    with pytest.raises(ValueError): r.advance("PROPOSE")

def test_runtime_does_not_grant_commit_early():
    r=AutopoiesisRuntime(cycle_id="c1")
    assert not r.can_commit()
    r=r.advance("DIAGNOSE")
    assert not r.can_commit()

def test_completed_cycle_cannot_advance():
    r=AutopoiesisRuntime(cycle_id="c1")
    for stage in ("DIAGNOSE","INVESTIGATE","PROPOSE","SHADOW","GOVERN","COMMIT"):
        r=r.advance(stage)
    with pytest.raises(ValueError): r.advance("DONE")
