# GNOSIS-V2 — Core Foundation

## Canonical engineering base for Gnozis research kernels and user products

Gnozis-V2 is the new engineering line of the Gnozis project. It is being developed as the future canonical Core foundation: a protected, testable computational base from which specialized research kernels and commercial user versions can later be assembled.

The older Gnozis repository is the project's Research Library. It contains historical research, reverse-analysis, mathematical models and experimental Python implementations. V2 is not merely a replacement archive; it is the engineering foundation that receives research-derived requirements after they have been formalized and mapped to code.

## Project relationship

Gnozis — Research Library
        ↓ discovered patterns / models / evidence
Gnozis-V2 — Core Foundation
        ├── Specialized Research Kernels
        └── Commercial User Versions

## Core rule

> Research can generate requirements; only implementation plus evidence establishes a Core capability.

## Current engineering foundation

The V2 line currently contains the protected Ψ=(X,R) state/evolution model, deep immutability and invariants, Candidate/Test/Verify/Authorize/Commit semantics, deterministic selection where applicable, budgets and stop conditions, instances/forks/lineage, SQLite persistence and durable provenance, append-only audit events, reflection/counterexamples/RuleProposal lineage/shadow evaluation, and boundaries preventing reflection from directly activating Core changes.

Exact status is governed by STATUS.md and current source/tests.

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

Conversely, philosophical or mathematical coherence is not proof of an implemented capability.

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
