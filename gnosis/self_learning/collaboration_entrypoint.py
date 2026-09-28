"""Single composition-root entrypoint for governed external collaboration actions.

This module deliberately contains no GitHub/network implementation. The application
composition root supplies already-trusted providers and an already-owned side-effect
capability. Request data never supplies providers or side-effect functions.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from .collaboration_authorization import TrustedEvidenceResolver, TargetRevisionResolver
from .collaboration_runtime import ExternalAction, TrustedCollaborationRuntime, build_trusted_collaboration_runtime


@dataclass(frozen=True)
class CollaborationComposition:
    """Immutable application-owned composition for external collaboration."""

    runtime: TrustedCollaborationRuntime

    def execute(self, **request: object) -> object:
        return self.runtime.execute(**request)


def compose_collaboration_runtime(
    *,
    target_revision_resolver: TargetRevisionResolver,
    evidence_resolver: TrustedEvidenceResolver,
    external_action: ExternalAction,
) -> CollaborationComposition:
    """Composition-root boundary.

    Only application bootstrap code should call this function. Request handlers
    should receive the resulting composition/runtime rather than provider inputs.
    """
    return CollaborationComposition(
        runtime=build_trusted_collaboration_runtime(
            target_revision_resolver=target_revision_resolver,
            evidence_resolver=evidence_resolver,
            external_action=external_action,
        )
    )
