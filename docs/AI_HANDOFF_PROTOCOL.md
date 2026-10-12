# Gnozis Core — AI Handoff & Continuation Protocol

## Purpose

This document defines the canonical mechanism for attaching a new AI system to Gnozis Core at any project stage without relying on conversation history, a previous agent's memory, or undocumented assumptions.

The repository is the durable project state. An AI session is replaceable.

## Canonical entry point

A newly connected AI must use this minimum recovery set, in order:

1. `docs/PROJECT_STATE.json` — machine-readable state snapshot, scope and staleness rule.
2. `docs/PHASE_LEDGER.md` — active phase, allowed/forbidden scope and transition rules.
3. `AI_CONTEXT.md` — operational architecture and research context.
4. `STATUS.md` — legacy status snapshot; historical claims are not current evidence.
5. `docs/AI_HANDOFF_PROTOCOL.md` — this continuation protocol.

Then fetch the live `main` HEAD and compare it with `docs/PROJECT_STATE.json::canonical_head`. Read `docs/MULTI_AGENT_BUILD_STRATEGY.md` and `AGENT_ROLES.md` as supporting governance context only; reconcile their role/tool assumptions against the active phase and current owner instructions. They do not override the phase ledger.

## Recovery sequence

```text
READ PROJECT_STATE + PHASE_LEDGER
    ↓
READ AI_CONTEXT + STATUS + HANDOFF PROTOCOL
    ↓
FETCH LIVE MAIN HEAD AND RECORD EXACT SHA
    ↓
COMPARE LIVE SHA WITH PROJECT_STATE.canonical_head
    ↓
IF STALE OR CONFLICTING: REPORT RECONCILIATION REQUIRED
    ↓
IDENTIFY ACTIVE PHASE / ALLOWED AND FORBIDDEN SCOPE
    ↓
INSPECT EXACT-HEAD CI AND RELEVANT EVIDENCE
    ↓
REPORT BASELINE + OPEN FINDINGS
    ↓
EXECUTE ONLY AN EXPLICIT TASK PERMITTED BY THE ACTIVE PHASE
```

A pinned `canonical_head` is a dated snapshot, not a live pointer. A SHA mismatch requires an explicit delta report; it does not authorize automatically rewriting the snapshot or changing scope.

A `next_permitted_action` string cannot override `forbidden_scope`. Starting work forbidden by the active phase requires a durable formal phase transition and explicit human owner authorization. Connector access and a prior AI statement are not architectural authority.

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

1. the exact current HEAD;
2. the active phase and its scope;
3. the latest independent verification state;
4. unresolved findings;
5. the next permitted action.

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

> Read `docs/PROJECT_STATE.json` and `docs/PHASE_LEDGER.md` first, then `AI_CONTEXT.md`, `STATUS.md`, and `docs/AI_HANDOFF_PROTOCOL.md`. Fetch live `main`, record its exact SHA, and compare it with the pinned `canonical_head`. Report any mismatch as `RECONCILIATION REQUIRED`. Determine implementation/verification/acceptance states, active phase, allowed and forbidden scope, latest tested commit, and open findings from repository evidence. Do not infer authority or current state from conversation history or free-text next-action fields. Report the baseline first, then execute only an explicitly assigned task permitted by the active phase.
