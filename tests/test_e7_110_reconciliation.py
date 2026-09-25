from gnosis.self_learning.e7_110_reconciliation import Metric, ReconciliationState, reconcile

def test_empty_metrics_block():
    r=reconcile(batch_id="B", acceptance_id="A", metrics=())
    assert r.state is ReconciliationState.BLOCKED

def test_matching_metrics_reconcile():
    r=reconcile(batch_id="B", acceptance_id="A", metrics=(Metric("M1",1,1),))
    assert r.state is ReconciliationState.RECONCILED
    assert r.snapshot_digest

def test_metric_discrepancy_blocks_promotion():
    r=reconcile(batch_id="B", acceptance_id="A", metrics=(Metric("M1",1,2),))
    assert r.state is ReconciliationState.CONFLICT

def test_same_inputs_produce_same_digest():
    m=(Metric("M1",1,1),Metric("M2",2,2))
    a=reconcile(batch_id="B", acceptance_id="A", metrics=m)
    b=reconcile(batch_id="B", acceptance_id="A", metrics=m)
    assert a.snapshot_digest == b.snapshot_digest
