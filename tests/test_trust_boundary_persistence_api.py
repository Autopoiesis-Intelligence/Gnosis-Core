import importlib

import pytest


def test_authoritative_persistence_is_not_public_storage_api():
    storage = importlib.import_module("gnosis.storage")
    assert not hasattr(storage, "persist_transition")
    with pytest.raises(ImportError):
        exec("from gnosis.storage import persist_transition", {})


def test_internal_persistence_primitive_remains_non_authoritative_storage_surface():
    repositories = importlib.import_module("gnosis.storage.repositories")
    assert hasattr(repositories, "_persist_transition")
