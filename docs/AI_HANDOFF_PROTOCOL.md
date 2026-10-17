# Gnozis Core — AI Handoff & Continuation Protocol

## Purpose

This document defines the canonical mechanism for attaching a new AI system to Gnozis Core at any project stage without relying on conversation history, a previous agent's memory, or undocumented assumptions.

The repository is the durable project state. An AI session is replaceable.

## Canonical entry point

A newly connected AI must first read these canonical state and phase records:

1. `docs/PROJECT_STATE.json` — machine-readable project state and pinned observation.
2. `docs/PHASE_LEDGER.md` — active phase, allowed scope, forbidden scope, and gates.
3. `docs/CONTEXT_CONTINUITY_CONTRACT.md` — snapshot freshness and reconciliation rules.

Then read the operational handoff set:

4. `docs/AI_HANDOFF_PROTOCOL.md` — this continuation protocol.
5. `AI_CONTEXT.md` — architecture and operating context.
6. `STATUS.md` — status claims, treated as snapshots until verified.
7. `docs/MULTI_AGENT_BUILD_STRATEGY.md` — governance and evidence model.
8. `AGENT_ROLES.md` — role and authority boundaries.

Fetch the live `main` HEAD and compare it with every pinned snapshot before relying on snapshot claims. If the live HEAD differs, or operational records conflict, report `RECONCILIATION REQUIRED`; inspect and record the exact delta before any deliberate snapshot refresh. Never silently rewrite a pinned SHA or infer missing evidence. After reconciliation, read only the specifications, source files and tests relevant to the assigned task.

## Recovery sequence

```text
READ PROJECT_STATE + PHASE_LEDGER + CONTINUITY CONTRACT
    ↓
FETCH LIVE MAIN HEAD
    ↓
COMPARE PINNED SNAPSHOTS; RECONCILE DELTAS
    ↓
READ HANDOFF + AI_CONTEXT + STATUS + GOVERNANCE
    ↓
IDENTIFY ACTIVE PHASE
    ↓
READ RELEVANT SOURCE / TESTS / CONTRACTS
    ↓
REPORT BASELINE + EVIDENCE
    ↓
WAIT FOR OR EXECUTE ONLY THE EXPLICIT TASK
```

## Mandatory session report

Before changing project files, a newly connected AI must be able to state:

```text
Repository:
Branch:
HEAD:
Implementation state:
Verification state:
Acceptance state:
Active phase:
Primary implementer:
Independent reviewer:
Final gate:
Allowed scope:
Forbidden scope:
Latest tested commit:
Open findings:
Next permitted action:
```

If these fields cannot be established from repository evidence, the AI must mark the missing items `UNKNOWN` or `UNVERIFIED` rather than infer them from historical conversation text.

## Three independent states

Never collapse these into one status:

```text
IMPLEMENTATION
    what exists in source

VERIFICATION
    what has been reproduced by tests/audit/CI

ACCEPTANCE
    what has passed the project integration gate
```

Examples:

- code may be `IMPLEMENTED` but `UNVERIFIED`;
- an artifact may be independently verified but not merged;
- a phase may be implemented and tested but still `NOT ACCEPTED`.

## Phase ledger

Every substantive phase must have an explicit record containing:

```text
Phase:
Objective:
Primary implementer:
Independent reviewer:
ChatGPT integration gate:
Allowed files:
Forbidden files:
Acceptance criteria:
Evidence required:
Current status:
Open findings:
```

A later AI continues the phase from this record instead of reconstructing intent from chat history.

## Artifact handoff

Any ZIP, patch, generated bundle, or external artifact used as engineering evidence must carry, in its accompanying report:

```text
Artifact filename:
SHA-256:
Baseline commit:
Producer:
Scope:
Files changed:
Files explicitly unchanged:
Test command:
Test result:
Verification status:
Acceptance status:
Known limitations:
```

An artifact without a verifiable baseline and contents is evidence of a claim, not proof of repository state.

## Access and authority

```text
access
  ↓
explicit task
  ↓
bounded implementation
  ↓
independent verification
  ↓
correction
  ↓
re-verification
  ↓
ChatGPT integration gate
```

GitHub or Google Drive access is an operational capability. It does not grant architectural authority.

No connected AI may infer permission to modify unrelated files from having write access.

## Runtime feedback

Gnozis is intentionally built while being exercised by connected AI systems and real runtime tests.

Runtime observations may produce:

- implementation defects;
- missing invariants;
- useful interfaces;
- new architectural requirements.

Runtime observations do **not** silently become canonical architecture. A new invariant or architectural requirement must be explicitly recorded and gated before becoming authoritative.

## Safe continuation rule

A replacement AI may continue an existing phase only after establishing:

1. the exact live `main` HEAD and the timestamped/pinned SHA in each operational snapshot;
2. any exact SHA delta and whether the state documents need a deliberate refresh;
3. the active phase and its allowed/forbidden scope;
4. the latest independently verified commit (or `UNKNOWN/UNVERIFIED`);
5. unresolved findings;
6. the next permitted action.

A SHA mismatch is a reconciliation signal, not an instruction to refresh automatically. JSON parsing or a successful document fetch does not prove runtime continuity.

If a previous agent stopped midway, continue from the last durable repository artifact and test evidence. Do not recreate work from memory and do not assume that an unfinished report means the code was completed.

## Core protection

The following are never changed merely to make an agent's task easier:

- `gnosis/core/*` semantics;
- persistence semantics;
- Memory/Core boundary;
- Identity/capability boundaries;
- security/encryption boundaries;
- Bridge/Core boundary;
- federation/trust semantics;
- self-modification/evolution rules.

Such changes require an explicit bounded task and subsequent independent verification.

## Current project rule

The canonical repository state always outranks an AI conversation. If documents disagree with source, the mismatch must be reported and resolved; it must not be silently rationalized.

The preferred evidence order is:

1. current source;
2. reproducible runtime behavior and real tests/CI;
3. accepted contracts/invariants;
4. independent audit evidence;
5. AI reports and proposals.

## Minimal continuation prompt

A new AI can be attached with the following operational instruction:

> Start with `docs/PROJECT_STATE.json`, `docs/PHASE_LEDGER.md`, and `docs/CONTEXT_CONTINUITY_CONTRACT.md`. Fetch the live `main` HEAD and reconcile pinned snapshot SHAs before relying on their claims. Then read `docs/AI_HANDOFF_PROTOCOL.md`, `AI_CONTEXT.md`, `STATUS.md`, `docs/MULTI_AGENT_BUILD_STRATEGY.md`, and `AGENT_ROLES.md`. Determine implementation, verification, and acceptance separately; identify the active phase, allowed and forbidden scope, latest independently verified commit (or `UNKNOWN/UNVERIFIED`), and open findings. Do not infer missing state from conversation history. Report the baseline first, then execute only the explicitly assigned bounded task.
