import sqlite3
import pytest

from gnosis.storage.database import connect
from gnosis.storage.repositories import StorageCorruptionError, load_world_observation, save_world_observation


def test_world_observation_round_trips_through_canonical_storage():
    conn = connect(":memory:")
    from gnosis.world import WorldObservation

    observation = WorldObservation(
        context_ref="zone",
        distinction="temperature",
        carrier_ref="sensor-1",
        properties={"value": 20, "unit": "C", "interval": [19.8, 20.2]},
        relations=("measures:room",),
    )

    save_world_observation(conn, observation)
    loaded = load_world_observation(conn, observation.observation_id)

    assert loaded == observation
    assert loaded.observation_id == observation.observation_id


def test_world_observation_conflicting_replay_fails_closed():
    conn = connect(":memory:")
    from gnosis.world import WorldObservation

    observation = WorldObservation(
        context_ref="zone",
        distinction="temperature",
        properties={"value": 20},
    )
    save_world_observation(conn, observation)

    conn.execute(
        "UPDATE world_observations SET properties=? WHERE observation_id=?",
        ('{"value":21}', observation.observation_id),
    )

    with pytest.raises(StorageCorruptionError, match="identity mismatch"):
        load_world_observation(conn, observation.observation_id)


def test_world_observation_storage_is_append_only():
    conn = connect(":memory:")
    from gnosis.world import WorldObservation

    observation = WorldObservation(
        context_ref="zone",
        distinction="temperature",
        properties={"value": 20},
    )
    save_world_observation(conn, observation)

    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "DELETE FROM world_observations WHERE observation_id=?",
            (observation.observation_id,),
        )
