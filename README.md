# GNOSIS CORE — Engineering Foundation

## Canonical engineering base for Gnozis research kernels and user products

Gnozis Core is the canonical engineering foundation of the Gnozis project: a protected, testable computational base from which specialized research kernels and commercial user versions can later be assembled.

The older Gnozis repository is the project's Research Library. It contains historical research, reverse-analysis, mathematical models and experimental Python implementations. The GitHub repository currently named Gnozis-V2 is the canonical Core repository; the product identity is Gnozis Core. It receives research-derived requirements only after they have been formalized and mapped to code.

## Project relationship

Gnozis — Research Library
        ↓ discovered patterns / models / evidence
Gnozis Core
        ├── Specialized Research Kernels
        └── Commercial User Versions

## Core rule

> Research can generate requirements; only implementation plus evidence establishes a Core capability.

## Current engineering foundation

The Core source currently contains the protected Ψ=(X,R) state/evolution model, recursive immutability mechanisms and invariants, Candidate/Test/Verify/Authorize/Commit semantics, deterministic selection where applicable, budgets and stop conditions, instances/forks/lineage, SQLite persistence and durable provenance, append-only audit events, reflection/counterexamples/RuleProposal lineage/shadow evaluation, and boundaries preventing reflection from directly activating Core changes.

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

Research-only hypotheses, domain-specific user features, philosophical interpretations, experimental mechanisms without a demonstrated Core requirement, an AI/LLM inside Ψ-Core, and autonomous rule activation without the required governance boundary.

## Verification principle

Documentation ≠ Source ≠ Test ≠ CI Evidence ≠ Runtime Evidence ≠ Audit.

No capability should be described as verified solely because a document or test file exists.

## Development principle

> First discover the structure. Then formalize it. Then implement the smallest reusable mechanism. Then prove what it actually does.


## Product boundary and current value

Gnozis Core is intended to become a reusable foundation for specialized research kernels and user/commercial products. The current product-facing contract is deliberately narrower than the long-term vision:

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

A connected AI product is a surface over the durable Gnozis context, not an alternative source of truth.


## Repository naming baseline

Product identity: **Gnozis Core**.

Canonical engineering role: **Core**.

Temporary second repository role: **Self-Learning Archive / Self-Learning Research & Learning Archive**.

The `Gnozis-V2` GitHub repository name is a current repository identifier, not the product/version identity. Physical GitHub renaming is an account-level repository operation and is not represented as completed by documentation alone.

## Partnership and specialized commercial cores

Gnozis Core is the common minimal engineering foundation. Self-Learning is intended to support two complementary partnership paths:

1. **Core-initiated development:** the Core identifies validated opportunities, missing capabilities or commercially relevant development directions and, through the governed contract pipeline, can prepare partner-facing development proposals.
2. **Partner-initiated specialization:** a partner may provide a project repository/specification and an agreed learning scope. The common Core can then serve as the minimal foundation for a separately specialized commercial core tuned to that partner's first tasks.

A specialized commercial core is not a second canonical Core. It is a bounded specialization:

`Gnozis Core + partner project specification + authorized learning/evidence -> specialized commercial core`

Partner-private data remains within the agreed trust boundary. Only explicitly shareable, validated and generalizable evidence may be eligible for integration back into common Self-Learning. A partner repository, learning database or generated contract block never becomes a second authority root and cannot directly mutate Ψ-Core.

The current partner-facing contract map is maintained in `docs/partners/CURRENT_PARTNER_CONTRACT_BLOCK.md` and refreshed by `scripts/update_partner_contract_block.py`. It is an index/briefing surface, not an authority or learning-proof artifact.
