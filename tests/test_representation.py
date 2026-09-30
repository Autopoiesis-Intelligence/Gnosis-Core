import pytest

from gnosis.world import Representation


def test_representation_is_immutable_and_content_identified():
    representation = Representation(
        encoding="json",
        media_type="application/json",
        content={"value": 20, "unit": "C"},
    )
    assert representation.representation_id == representation.content_digest
    with pytest.raises(TypeError):
        representation.content["value"] = 21


def test_representation_identity_ignores_mapping_order():
    a = Representation(encoding="json", content={"value": 20, "unit": "C"})
    b = Representation(encoding="json", content={"unit": "C", "value": 20})
    assert a.representation_id == b.representation_id


def test_representation_does_not_claim_epistemic_status():
    representation = Representation(encoding="text", content="20 C")
    assert not hasattr(representation, "status")
    assert not hasattr(representation, "evidence")
