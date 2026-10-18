"""Bounded, deterministic engineering task candidate generation."""

from .generator import TaskGenerationError, generate_task_candidate

__all__ = ["TaskGenerationError", "generate_task_candidate"]
