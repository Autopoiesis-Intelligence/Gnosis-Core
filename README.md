# GNOSIS CORE — Engineering Foundation

## Canonical engineering base for Gnosis research kernels and user products

Gnosis-Core is the engineering foundation of the Gnosis project: a testable computational base from which specialized research kernels and commercial user versions may later be assembled. This repository is currently public on GitHub; documentation must not describe the repository itself as private or protected.

`Gnosis` is the public product and evidence surface; `Gnosis-Memory` is the research/context surface. `Gnosis-Genesis` is a separate private repository with a declared factory/orchestration role. Its existence and privacy do not by themselves prove an operational end-to-end factory or grant authority to change Core. Research-derived requirements enter engineering only after they have been formalized and mapped to code.

## Project relationship

Gnosis
        ↓ public product / evidence
Gnosis-Memory
        ↓ research / context / provenance
Gnosis-Core
        ↓ reviewed requirements and contracts
Gnosis-Genesis
        ↓ candidate modules / proposals
independent verification and governed release

## Core rule

> Research can generate requirements; only implementation plus evidence establishes a Core capability.

## Current engineering foundation

The Core source currently contains the Ψ=(X,R) state/evolution model, recursive immutability mechanisms and invariants, Candidate/Test/Verify/Authorize/Commit semantics, deterministic selection where applicable, budgets and stop conditions, instances/forks/lineage, SQLite persistence and durable provenance, append-only audit events, reflection/counterexamples/RuleProposal lineage/shadow evaluation, and boundaries preventing reflection from directly activating Core changes.

These statements describe repository capabilities present in source; they are not, by themselves, claims of fresh runtime/CI verification. Exact acceptance status is governed by STATUS.md, current source/tests, and reproducible evidence.

## Research-to-product pipeline

Research observation
→ Pattern discovery
→ Definition / formalization
→ Falsifiable consequence
→ Engineering gap
→ Core implementation
→ Tests / CI / runtime evidence
→ Specialized kernel
→ User / commercial product

A research idea is not considered unrealizable merely because it is not currently implemented. Feasibility is established by formalization, architecture mapping, constraints and evidence.

Conversely, conceptual or mathematical coherence is not proof of an implemented capability.

## What belongs in Core

The Core should contain reusable mechanisms fundamental across multiple future kernels and products: state semantics, protected transitions, verification, provenance, persistence semantics, governed evolution and other demonstrated foundational capabilities.

Domain-specific behavior normally belongs above Core in a specialized kernel or product layer.

## What does not enter Core automatically

Research-only hypotheses, domain-specific user features, philosophical interpretations, experimental mechanisms without a demonstrated Core requirement, an AI/LLM inside the trusted Core runtime, and autonomous rule activation without the required governance boundary.

## Verification principle

Documentation ≠ Source ≠ Test ≠ CI Evidence ≠ Runtime Evidence ≠ Audit.

No capability should be described as verified solely because a document or test file exists.

## Development principle

> First discover the structure. Then formalize it. Then implement the smallest reusable mechanism. Then prove what it actually does.


## Product boundary and current value

Gnosis-Core is intended to become a reusable foundation for specialized research kernels and user/commercial products. The current product-facing contract is deliberately narrower than the long-term vision:

- preserve durable task/project context independently of the connected AI product;
- keep evidence and provenance addressable independently of the interface that produced them;
- distinguish observation, explanation, governance and authorization;
- allow reflection to generate bounded proposals without allowing proposals to activate themselves;
- preserve rejected, uncertain and insufficient-evidence outcomes as usable project history.

This makes the current product direction a **governed knowledge/evolution substrate**, not an autonomous self-modifying assistant. Product features that require identity, memory, connectors, federation, encryption or autonomous activation remain explicitly outside the accepted Core capability set until their contracts and runtime evidence are completed.

### Product improvement rule

Every product-facing capability should answer four questions:

1. What durable user value does it provide?
2. What evidence establishes that it works?
3. What authority does it receive, if any?
4. What happens when evidence is missing, stale, conflicting or revoked?

A connected AI product is a surface over the durable Gnosis context, not an alternative source of truth.


## Repository naming baseline

Product identity: **Gnosis**.

Separate private workspace: **Gnosis-Genesis — declared factory/orchestration role; operational capabilities require current implementation, CI and runtime evidence**.

Research-memory role: **Gnosis-Memory**.

The historical `Gnozis-V2` naming is retired from product documentation. Historical references may remain in provenance records where they identify an older repository state, but must not be used as the current product identity.

## Partnership and specialized commercial cores

Gnosis-Core is the common minimal engineering foundation. Self-Learning is intended to support two complementary partnership paths:

1. **Core-initiated development:** the Core identifies validated opportunities, missing capabilities or commercially relevant development directions and, through the governed contract pipeline, can prepare partner-facing development proposals.
2. **Partner-initiated specialization:** a partner may provide a project repository/specification and an agreed learning scope. The common Core can then serve as the minimal foundation for a separately specialized commercial core tuned to that partner's first tasks.

A specialized commercial core is not a second canonical Core. It is a bounded specialization:

`Gnosis-Core + partner project specification + authorized learning/evidence -> specialized commercial core`

Partner-private data remains within the agreed trust boundary. Only explicitly shareable, validated and generalizable evidence may be eligible for integration back into common Self-Learning. A partner repository, learning database or generated contract block never becomes a second authority root and cannot directly mutate trusted Core state.

The current partner-facing contract map is maintained in `docs/partners/CURRENT_PARTNER_CONTRACT_BLOCK.md` and refreshed by `scripts/update_partner_contract_block.py`. It is an index/briefing surface, not an authority or learning-proof artifact.
