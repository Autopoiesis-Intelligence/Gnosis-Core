import pytest

from gnosis.world import Measurement


def test_measurement_is_content_identified():
    m = Measurement(quantity="temperature", magnitude=20, unit="C", scale="celsius")
    assert m.measurement_id


def test_measurement_requires_minimal_quantitative_structure():
    with pytest.raises(ValueError):
        Measurement(quantity="", magnitude=20, unit="C")
    with pytest.raises(ValueError):
        Measurement(quantity="temperature", magnitude=20, unit="")


def test_measurement_rejects_boolean_as_magnitude():
    with pytest.raises(TypeError):
        Measurement(quantity="temperature", magnitude=True, unit="C")


def test_measurement_has_no_epistemic_authority():
    m = Measurement(quantity="temperature", magnitude=20, unit="C")
    assert not hasattr(m, "status")
    assert not hasattr(m, "evidence")
