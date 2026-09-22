import pytest
from gnosis.core.domain_lineage import bind_domain_lineage

def ids():
    return dict(cycle_id="c1",gap_id="g1",investigation_id="i1",proposal_id="p1",
                evaluation_id="e1",authorization_id="a1",transition_id="t1")

def test_domain_lineage_binds_all_real_artifact_ids():
    l=bind_domain_lineage(**ids())
    assert l.cycle_id=="c1"
    assert l.refs()==("g1","i1","p1","e1","a1","t1")

def test_domain_lineage_rejects_missing_identity():
    x=ids(); x["transition_id"]=""
    with pytest.raises(ValueError): bind_domain_lineage(**x)

def test_domain_lineage_rejects_duplicate_identity():
    x=ids(); x["proposal_id"]="g1"
    with pytest.raises(ValueError): bind_domain_lineage(**x)
