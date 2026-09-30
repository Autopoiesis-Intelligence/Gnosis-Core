import pytest

from gnosis.world import WorldObservation


def test_world_observation_supported_value_domain_is_stable():
    a = WorldObservation(
        context_ref="zone",
        distinction="temperature",
        properties={
            "null": None,
            "bool": True,
            "integer": 20,
            "float": 20.25,
            "text": "C",
            "nested": {"b": [1, 2, 3], "a": {"x": False}},
        },
    )
    b = WorldObservation(
        context_ref="zone",
        distinction="temperature",
        properties={
            "nested": {"a": {"x": False}, "b": [1, 2, 3]},
            "text": "C",
            "float": 20.25,
            "integer": 20,
            "bool": True,
            "null": None,
        },
    )
    assert a.observation_id == b.observation_id


def test_world_observation_rejects_arbitrary_python_values():
    class Arbitrary:
        pass

    with pytest.raises(TypeError):
        WorldObservation(
            context_ref="zone",
            distinction="temperature",
            properties={"value": Arbitrary()},
        )


def test_world_observation_identity_survives_reconstruction():
    original = WorldObservation(
        context_ref="zone",
        distinction="temperature",
        carrier_ref="sensor-1",
        properties={"value": 20, "unit": "C", "interval": [19.8, 20.2]},
        relations=("measures:room",),
    )
    reconstructed = WorldObservation(
        context_ref="zone",
        distinction="temperature",
        carrier_ref="sensor-1",
        properties={"value": 20, "unit": "C", "interval": [19.8, 20.2]},
        relations=("measures:room",),
    )
    assert reconstructed.observation_id == original.observation_id
