# Core Typing and Reproducibility Contract

## Objective
Increase static confidence and make the Core environment reproducible without prescribing a specific package manager.

## Typing
Public Core interfaces MUST have explicit type annotations.
The project SHOULD progressively enforce strict static analysis where compatible with architecture and dependencies.
Any deliberate strict-mode exclusion MUST be documented.

## Reproducibility
Build/test dependencies MUST be declared in pyproject.toml and locked or otherwise reproducibly resolved.
CI MUST exercise the declared supported Python versions.
Dependency changes require review of Core trust boundaries and reproducibility.

Poetry, uv, setuptools or another supported build mechanism may be used; the contract concerns reproducibility, not tool branding.

## Acceptance
Produce a reproducible environment definition, static-analysis configuration, CI evidence and documented exceptions.

Status: DESIGNED / NOT_IMPLEMENTED.
