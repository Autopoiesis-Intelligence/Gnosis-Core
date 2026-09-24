import pytest
from dataclasses import FrozenInstanceError, replace
from gnosis.self_learning.collaboration_proposal import generate_collaboration_proposal,github_publication_eligible,privacy_safe

def make(channel="COMMERCIAL"):
    return generate_collaboration_proposal(contract_id="sha256:contract",channel=channel,title="Bounded partner project",objective="Train a specialized Core",scope="partner:demo",evidence_refs=("evidence:1",),requested_inputs=("brief",),deliverable_contract_refs=("E7.69",),publication_target="github:proposal",revision="r1")

def test_commercial_and_open_channels_are_explicit():
    assert make("COMMERCIAL").channel=="COMMERCIAL"
    assert make("OPEN").channel=="OPEN"

def test_github_publication_requires_external_governance():
    assert github_publication_eligible(proposal=make(),reviewed=True,authorized=True)
    assert not github_publication_eligible(proposal=make(),reviewed=False,authorized=True)
    assert not github_publication_eligible(proposal=make(),reviewed=True,authorized=False)

def test_private_data_blocks_publication_safety():
    assert privacy_safe(proposal=make(),private_data_refs=())
    assert not privacy_safe(proposal=make(),private_data_refs=("partner:private",))

def test_identity_is_deterministic():
    assert make()==make()

def test_invalid_channel_rejected():
    with pytest.raises(ValueError): make("PRIVATE")

def test_proposal_is_immutable():
    with pytest.raises(FrozenInstanceError): make().title="attacker"

def test_evidence_tampering_changes_identity():
    original=make()
    assert replace(original,evidence_refs=("evidence:attacker",)).proposal_id != original.proposal_id

def test_contract_and_revision_tampering_changes_identity():
    original=make()
    assert replace(original,contract_id="sha256:foreign").proposal_id != original.proposal_id
    assert replace(original,revision="r2").proposal_id != original.proposal_id

def test_status_and_authority_cannot_be_self_promoted():
    proposal=make()
    assert proposal.status=="PROPOSED"
    assert proposal.authority=="proposal-only"
    assert not github_publication_eligible(proposal=proposal,reviewed=False,authorized=False)

def test_private_refs_are_never_publication_safe():
    assert privacy_safe(proposal=make(),private_data_refs=("partner:private","credential:secret")) is False
