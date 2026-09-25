# Runtime adapter boundary

The first runtime adapter must call the existing Core execution surface; it must not
reimplement Engine, State, TransitionRecord, persistence, provenance, or commit logic.

## Current baseline observation

At the inspected baseline, `gnosis.core.evolution.Engine.history` is an in-process
Python list. Repository documentation explicitly states that it is not a persistent,
hash-chained audit log. Therefore this contract must distinguish in-process mutation
boundary checks from durable audit claims.

## Adapter requirements

1. Import the canonical Core API.
2. Construct only through the existing public execution path.
3. Execute one canonical transition.
4. Execute negative cases through the existing public API where supported.
5. Capture before/after state digests and transition record data.
6. Never mutate `Engine.history` directly.
7. Never instantiate a second mutation authority.
8. Report unsupported negative cases as NOT_IMPLEMENTED rather than PASS.

## Evidence

The adapter must record the exact Core revision and the executed test identifiers.
