from gnosis.core.identity_contracts import IDENTITY_MATRIX

def test_identity_matrix_covers_evolution_chain():
    assert [x.name for x in IDENTITY_MATRIX]==["State","Candidate","Transition","Provenance","RecoveryCheckpoint"]
    assert all(x.primary_identity and x.persistence_identity and x.lineage_binding and x.evidence_binding for x in IDENTITY_MATRIX)

def test_identity_matrix_does_not_use_rowid_as_identity():
    assert all("rowid" not in (x.primary_identity+x.persistence_identity+x.lineage_binding).lower() for x in IDENTITY_MATRIX)
