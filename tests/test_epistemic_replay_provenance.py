import sqlite3
import pytest

from gnosis.storage.database import connect
from gnosis.storage.repositories import (
    _append_epistemic_transition,
    StorageCorruptionError,
)
from gnosis.world import EpistemicReplay, EpistemicState, TransitionAuthority


def test_durable_replay_requires_matching_audit_provenance():
    conn = connect(":memory:")
    t = TransitionAuthority.create(
        subject_ref="observation:1",
        from_state=EpistemicState.OBSERVED,
        to_state=EpistemicState.SUPPORTED,
        basis_refs=("evidence:1",),
    )
    _append_epistemic_transition(conn, t)
    conn.execute("DELETE FROM audit_events WHERE transition_id=?", (t.transition_id,))
    with pytest.raises(StorageCorruptionError, match="audit mismatch"):
        EpistemicReplay.reconstruct_from_ledger(
            conn, "observation:1", EpistemicState.OBSERVED
        )
