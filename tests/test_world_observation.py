from gnosis.world import WorldObservation


def test_world_observation_is_immutable_and_content_identified():
    observation = WorldObservation(
        context_ref="sensor_zone_4",
        distinction="temperature",
        carrier_ref="sensor_4",
        properties={"value": 20, "unit": "C"},
        relations=("measures:room_4",),
    )

    assert observation.observation_id == observation.content_digest

    try:
        observation.properties["value"] = 21
        raise AssertionError("nested properties must be immutable")
    except TypeError:
        pass


def test_world_observation_identity_ignores_mapping_order():
    a = WorldObservation(
        context_ref="sensor_zone_4",
        distinction="temperature",
        properties={"value": 20, "unit": "C"},
    )
    b = WorldObservation(
        context_ref="sensor_zone_4",
        distinction="temperature",
        properties={"unit": "C", "value": 20},
    )

    assert a.observation_id == b.observation_id


def test_world_observation_does_not_contain_epistemic_status():
    observation = WorldObservation(
        context_ref="sensor_zone_4",
        distinction="temperature",
        properties={"value": 20, "unit": "C"},
    )

    assert not hasattr(observation, "status")
