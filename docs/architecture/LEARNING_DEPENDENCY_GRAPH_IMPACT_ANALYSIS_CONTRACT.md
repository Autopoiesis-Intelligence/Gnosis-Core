# E7.19 — Learning Dependency Graph and Impact Analysis Contract

## Objective

Make dependency propagation explicit so that changes to sources, evidence, agents, proposals, tests, rules, policies, or parent states identify all derived learning artifacts that may require re-evaluation.

## Dependency graph

Represent learning lineage as a directed graph:

G_L = (V, E)

where V contains sources, revisions, evidence, findings, counterexamples, candidates, proposals, evaluations, tests, rules, policies and state transitions.

An edge u -> v means that v depends materially on u.

## Impact closure

For changed node x, define:

Impact(x) = Descendants_G_L(x)

Every materially affected descendant MUST be classified as:

- REVALIDATE;
- SUSPEND;
- REVOKE;
- SUPERSEDE;
- HISTORICAL_ONLY;
- UNAFFECTED, with evidence for the classification.

## Dependency types

Edges MUST distinguish at least:

- DERIVED_FROM;
- TESTED_BY;
- EVALUATED_AGAINST;
- GOVERNED_BY;
- DEPENDS_ON_STATE;
- AUTHORIZED_BY;
- SUPERSEDES.

## No hidden dependency

A rule MUST NOT be considered unaffected merely because no explicit dependency edge was recorded if its evaluation relied on the changed artifact. Missing provenance is a revalidation failure, not proof of independence.

## Cross-repository dependencies

Partner repositories/datasets may participate as source nodes. Their immutable revision is part of the graph identity.

A new partner revision creates a new source node; it does not mutate the previous node.

## Change propagation

Source revocation, revision change, agent capability change, policy change, Core invariant change, or parent-state change MUST trigger impact analysis before affected learned rules remain active.

## Acceptance

Tests must demonstrate deterministic impact closure, multi-hop propagation, cross-repository source changes, missing-edge handling, supersession and restart/replay of the dependency graph.

Status: DESIGNED / NOT_IMPLEMENTED.
