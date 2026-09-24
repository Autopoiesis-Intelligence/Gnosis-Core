import pytest
from gnosis.self_learning.provenance_closure import close_provenance,replay_matches,may_verify,creates_execution_authority
def make(): return close_provenance(chain_refs=("proposal","contract","execution","verification","learning"),chain_digests=("d1","d2","d3","d4","d5"))
def test_closure_has_final_digest(): assert make().final_digest.startswith("sha256:")
def test_identical_replay_matches():
 c=make(); assert replay_matches(closure=c,replay_chain_refs=c.chain_refs,replay_chain_digests=c.chain_digests) and may_verify(closure=c,replay_chain_refs=c.chain_refs,replay_chain_digests=c.chain_digests)
def test_changed_digest_fails():
 c=make(); bad=list(c.chain_digests); bad[2]="tampered"; assert not replay_matches(closure=c,replay_chain_refs=c.chain_refs,replay_chain_digests=bad)
def test_changed_order_fails():
 c=make(); assert not replay_matches(closure=c,replay_chain_refs=tuple(reversed(c.chain_refs)),replay_chain_digests=tuple(reversed(c.chain_digests)))
def test_length_mismatch_blocks():
 with pytest.raises(ValueError): close_provenance(chain_refs=("a",),chain_digests=())
def test_no_authority(): assert not creates_execution_authority(closure=make())
def test_deterministic(): assert make()==make()
