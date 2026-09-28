# Gnosis-Core → Gnosis-Genesis Separation Plan

Status: ACTIVE — classification only; no code moved in this step.

## Current boundary

`Gnosis-Core` remains the only canonical authority-bearing runtime.

`Gnosis-Genesis` is the protected module-factory/commercial layer. It must not become a second canonical state authority.

## Keep in Gnosis-Core

- `gnosis/core/`
- `gnosis/evolution/`
- `gnosis/storage/`
- `gnosis/instances/`
- bounded runtime portions of `gnosis/reflection/`
- `gnosis/context/` where it serves canonical task/context continuity
- tests proving Core behavior
- CI and architecture gates
- current Core contracts and operational governance

These paths participate directly in canonical state, transitions, persistence, recovery, admission, or execution authority.

## Candidate for Gnosis-Genesis

- private Genesis orchestration/factory mechanisms
- proprietary module-generation logic
- commercial/private configuration logic
- sensitive diagnostic or factory corpus that is not required for public operation
- private routing/configuration that must not become a public dependency

A candidate is not moved merely because a filename contains “Genesis”.

## Candidate for Gnosis-Memory / Gnosis-Research

- `diagnostic_corpus/` after provenance-preserving extraction
- historical audit material only after active CI/audit evidence remains addressable
- sanitized research/evidence material

The destination must preserve source commit, scenario identity, generation method, verification status and relationship to the Core baseline.

## Public documentation

Public contracts can be exported to the public repositories only after removing private implementation details, secrets, tenant data, commercial logic and authority-bearing internals.

## Non-negotiable dependency direction

    Gnosis-Core
        ↓
    Gnosis-Genesis
        ↓
    public/product/research/knowledge/commercial adapters

`Gnosis-Core` must not import or require `Gnosis-Genesis`, `Gnosis-Research`, `Gnosis-Memory`, external AI, connectors, or commercial services.

Genesis may propose modules, evidence or changes; only the Core authority path can admit canonical state changes.

## Migration gate

For every moved module:
1. responsibility is singular;
2. dependency direction is valid;
3. trust authority is unchanged;
4. data sensitivity is classified;
5. existing evidence remains traceable;
6. replacement is tested before old implementation is removed;
7. rollback preserves provenance.

## Immediate next extraction

`diagnostic_corpus/` is the first concrete extraction candidate.

Do not move it yet. First create the Research destination contract and provenance manifest, then verify that current Core tests and audit references remain addressable.

## Naming cleanup

This document uses current repository names: `Gnosis-Core`, `Gnosis-Genesis`, `Gnosis-Memory`, `Gnosis-Research`, `Gnosis-Knowledge`, `Gnosis-Exchange`, `Gnosis-Sdk`, and `Gnosis`.

Historical documents containing `Gnozis`, `Gnozis-V2`, `Genesis/Genezis`, or former repository names are historical evidence until explicitly updated; they must not silently redefine the current topology.