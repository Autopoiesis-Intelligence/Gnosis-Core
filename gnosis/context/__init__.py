"""Task-context domain models and errors.

Persistence is exposed through gnosis.ports.repositories.TaskContextRepositoryPort
and infrastructure adapters, not as a public concrete SQLite repository.
"""
from .handoff import ContextHandoff
from .model import TaskContext
from .repository import ContextNotFound, ContextRevisionConflict

__all__ = ["ContextHandoff", "TaskContext", "ContextNotFound", "ContextRevisionConflict"]
