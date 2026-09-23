# Mathematical / Code Alignment — R1

## Purpose

This document records the bounded R1 modernization that makes the implemented Core representation explicitly match the current mathematical reading of Ψ=(X,R). It does not introduce a second state model.

## Canonical mapping

| Mathematical object | Runtime representation | Semantics |
|---|---|---|
| X | `State.elements` | immutable mapping from element identity to element data |
| R | `State.relations` | immutable, canonicalized set-like collection of `Relation` values |
| Ψ | `State.content_id` / `State.psi_id` | content identity of `(X,R)`, independent of lineage version |
| lineage/runtime metadata | `State.version` | versioning metadata, excluded from Ψ content identity |
| candidate Ψ′ | `Candidate.proposed_state` | proposed successor state |
| transition provenance | `TransitionRecord` | historical execution/audit record, not a second state model |

## Relation semantics

R is treated as a mathematical relation collection rather than an ordered event stream.

At construction time Core:
- deep-freezes element data;
- removes duplicate relations by stable `relation_id`;
- canonicalizes relation ordering by `relation_id`;
- rejects negative lineage versions.

Therefore relation ordering and duplicate representation cannot create a new Ψ.

## Identity distinction

`State.state_id` identifies a versioned runtime state and includes `version`.

`State.content_id` and `State.psi_id` identify the mathematical content `(X,R)` and exclude `version`.

Thus two historical states may represent the same mathematical Ψ while remaining different lineage states. This distinction is intentional and prevents version metadata from being mistaken for mathematical evolution.

## Evolution gate

The implemented transition remains:

`Candidate → Test/Invariant Evaluation → Commit`

with the mathematical requirement:

`Ψ′ != Ψ`

implemented by the `meaningful_change` invariant through `content_id` comparison.

Additional protected conditions remain:
- candidate parent must match the current versioned state;
- every relation endpoint must reference an element in the proposed X;
- proposed version must strictly increase;
- custom Test predicates must return an actual boolean;
- protected invariants cannot be bypassed by a custom Test.

## Explicit non-claims

This R1 alignment does not establish:
- causal correctness of a Test predicate;
- formal theorem-prover verification;
- autonomous endogenous generation;
- governance/activation authority;
- universal validity of Ψ=(X,R) outside the bounded Core model.

The modernization is accepted only as a code/mathematics alignment improvement and remains subject to runtime/CI verification on the resulting commit.