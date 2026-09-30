import pytest

from gnosis.world import WorldRelation


def test_world_relation_is_content_identified():
    relation = WorldRelation(
        subject_ref="observation:1",
        predicate="measures",
        object_ref="measurement:1",
        context_ref="room-4",
    )
    assert relation.relation_id


def test_world_relation_requires_explicit_endpoints_and_predicate():
    with pytest.raises(ValueError):
        WorldRelation(subject_ref="", predicate="measures", object_ref="measurement:1")
    with pytest.raises(ValueError):
        WorldRelation(subject_ref="observation:1", predicate="", object_ref="measurement:1")
    with pytest.raises(ValueError):
        WorldRelation(subject_ref="observation:1", predicate="measures", object_ref="")


def test_world_relation_has_no_epistemic_authority():
    relation = WorldRelation(
        subject_ref="observation:1",
        predicate="measures",
        object_ref="measurement:1",
    )
    assert not hasattr(relation, "status")
    assert not hasattr(relation, "evidence")
