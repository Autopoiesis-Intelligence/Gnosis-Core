# Gnozis Core — Phase Ledger

This ledger is the durable continuation record for substantive project phases.

It exists so a replacement AI can continue from repository evidence rather than conversation history.

## Current phase

### CONTEXT-CONTINUITY ARCHITECTURE

**Status:** DOCUMENTATION_AND_ARCHITECTURE

**Objective:**
Build the durable project-context layer that allows a newly connected AI product to recover the real project state, distinguish implementation from verification and acceptance, and continue bounded work without depending on a previous conversation.

**Primary implementer:** ChatGPT

**Independent reviewer:** NOT_ASSIGNED

**Integration gate:** ChatGPT under explicit human project-owner authorization

**Allowed scope:**
- context recovery contracts;
- AI handoff protocol;
- machine-readable project state;
- phase/evidence ledger design;
- documentation required for cross-product continuation;
- architectural analysis of how connected products can consume the same durable project state.

**Forbidden scope:**
- Memory corrective implementation;
- Core semantic changes;
- Identity/authentication/authorization implementation;
- encryption implementation;
- Internet Bridge implementation;
- federation implementation;
- autonomous self-modification.

## State at phase entry

- Persistence: accepted in `main`.
- Multi-agent strategy: `PASS WITH FINDINGS`; current working governance model.
- Memory: `NOT ACCEPTED`; external artifact remains outside `main` pending corrective pass and independent re-audit.
- Context Continuity: architecture/documentation layer; cross-product execution test remains outstanding.

## Required evidence

A continuation-capable AI must be able to recover:

```text
repository
branch
current HEAD
latest independently tested commit
active phase
active task
implementation state
verification state
acceptance state
primary implementer
independent reviewer
integration gate
allowed scope
forbidden scope
open findings
next permitted action
```

Every material claim must be traceable to durable repository evidence or explicitly marked `UNKNOWN` / `UNVERIFIED`.

## Evidence precedence

```text
current source
    ↓
reproducible runtime behavior / real CI
    ↓
accepted contracts and invariants
    ↓
independent audit evidence
    ↓
AI reports / proposals
    ↓
conversation history
```

Conversation history is not a canonical project-state source.

## Acceptance gate: explicit exit criteria

Acceptance is **BLOCKED** while the independent reviewer is `NOT_ASSIGNED`. This is a deliberate hold, not permission to treat the ChatGPT integration gate as independent review.

Before this phase can be marked accepted, the project record must contain all of the following for the exact patch-head SHA:

1. **Implementation identity:** exact repository, branch, patch-head SHA, and the relevant change set.
2. **Verification evidence:** completed CI/runtime results tied to that SHA, including failures and cancelled checks; a successful documentation parse alone is insufficient.
3. **Independent review:** a reviewer explicitly assigned through the project owner's authorized process, with a recorded review result and unresolved findings. The implementer cannot self-label this evidence independent.
4. **Integration gate:** the result of the ChatGPT integration gate, recorded separately from independent review and under explicit human project-owner authorization.
5. **Decision record:** an explicit acceptance decision with the evidence references and any remaining limitations. If any required item is missing, contradictory, or unverified, acceptance remains `NOT_ACCEPTED`.

Assigning a reviewer, authorizing a phase transition, and accepting the result are separate decisions. None is implied by a mergeable PR, a passing subset of checks, or the completion of implementation work.

## Transition rule

A phase may move from implementation to verification only when the implementation artifact is available at a reproducible repository state or verifiable external artifact.

A phase may move from verification to acceptance only after the required independent verification evidence exists and the integration gate is explicitly recorded.

A new AI may continue an existing phase only after reading the canonical handoff documents and reporting the current baseline.

## Cross-product continuation objective

The intended user architecture is:

```text
User
  ↓
any connected AI/product
  ↓
canonical project context + permitted project resources
  ↓
real current state
  ↓
bounded task execution
  ↓
reproducible evidence
  ↓
shared project state
```

Google Drive, GitHub, or another connected product is a project resource/interface, not a separate source of truth unless explicitly designated for a specific artifact.

A connected AI must not treat access to a resource as authority to change architecture.

## Next permitted gate

Continue only within the active `CONTEXT-CONTINUITY ARCHITECTURE` phase:

1. Reconcile operational handoff documents and machine-readable snapshots.
2. Validate JSON syntax, duplicate-key absence, required existing fields/types, canonical links, and consistency with this phase's allowed/forbidden scope.
3. Record exact patch-head SHA and available CI/runtime evidence.
4. Keep acceptance `NOT_ACCEPTED` until the explicitly required acceptance gate is recorded.

Memory corrective implementation and Memory re-audit are outside this phase's permitted scope. They require a separately recorded, owner-approved phase transition before they can become a next action. The independent reviewer remains `NOT_ASSIGNED`; ChatGPT's integration gate is not independent verification.

## Snapshot rule

This ledger is durable evidence, not a substitute for checking the live repository. At every new session the AI must verify the current `main` HEAD before relying on any pinned snapshot value.
