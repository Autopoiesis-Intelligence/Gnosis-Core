import pytest
from gnosis.core.artifact_runtime import ArtifactBackedRuntime, RuntimeArtifact

def a(stage,key): return RuntimeArtifact(stage,{key:"id:"+key})

def test_each_stage_requires_its_artifact():
    r=ArtifactBackedRuntime(cycle_id="c")
    for stage,key,next_stage in (
        ("DIAGNOSE","gap_id","INVESTIGATE"),
        ("INVESTIGATE","investigation_id","PROPOSE"),
        ("PROPOSE","proposal_id","SHADOW"),
        ("SHADOW","evaluation_id","GOVERN"),
        ("GOVERN","authorization_id","COMMIT"),
        ("COMMIT","transition_id","DONE"),
    ):
        assert r.stage==stage
        r=r.advance(a(stage,key))
        assert r.stage==next_stage

def test_missing_artifact_blocks_progress():
    with pytest.raises(ValueError): ArtifactBackedRuntime().advance(
        RuntimeArtifact("DIAGNOSE",{})
    )

def test_wrong_stage_artifact_blocks_progress():
    with pytest.raises(ValueError): ArtifactBackedRuntime().advance(
        a("PROPOSE","proposal_id")
    )

def test_empty_reference_blocks_progress():
    with pytest.raises(ValueError): ArtifactBackedRuntime().advance(
        RuntimeArtifact("DIAGNOSE",{"gap_id":""})
    )
