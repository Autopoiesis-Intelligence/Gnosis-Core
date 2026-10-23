# Gnosis-Core — AI Agent Roles and Authority

## Current operating model

The owner's target stack (2026-10-23) applies to all Autopoiesis-Intelligence repositories:

- **Claude** is the main engineer: implementation, code and CI fixes, tests, pull requests and review follow-up.
- **ChatGPT / GPT-Codex** provide architecture control and independent audit of exact SHAs, tests, CI and execution evidence.
- **Copilot** is the self-update executor inside the autopoiesis-core protocol.
- **GitHub** is the canonical state of code, tasks, PRs and history; GitHub Actions results are the evidence that automation ran.

No agent merges to `main` without the owner's explicit permission. The canonical description of roles is `docs/OPERATING_MODEL.md` in autopoiesis-core. Other AI services are not active participants unless the owner explicitly reactivates them.

Access to repository data is not the same as authority to change protected state. A tool connection, generated patch, test result, or recommendation does not independently grant execution authority.

## Responsibilities

### Project owner

- defines product intent and may authorize substantive work;
- retains control over external accounts, secrets, signing keys, and any action that requires unavailable credentials or an explicit external confirmation;
- may change the active tool policy at any time.

### External tools and connected services

- provide bounded read/write operations according to their actual permissions;
- do not become an authority root merely because they are connected;
- must not receive secrets or protected data beyond the authorized task scope.

## Evidence hierarchy

When reports conflict, reconcile against:

1. exact current source and commit SHA;
2. reproducible tests and actual CI runs;
3. runtime and persisted evidence where relevant;
4. accepted project contracts and invariants;
5. audit findings and design proposals;
6. conversation summaries, which are recovery context rather than proof.

The project evidence ladder is:

**DESIGN → IMPLEMENTED → REACHABLE → RUNTIME → PERSISTED → AUDITED → CI_PROVEN**

A status, percentage, or readiness claim is not proven without the corresponding exact source and evidence. Local tests, synthetic fixtures, or a green unrelated workflow do not establish production runtime behavior.

## Core protection

The following require explicit scope and evidence-based review:

- execution authorization and trusted policy inputs;
- state transitions and commit gates;
- persistence and replay semantics;
- identity, signatures, keys, expiry, revocation, and replay protection;
- evolution identity and provenance;
- any mechanism that could activate a proposal or modify protected state.

A proposal, approval record, signature-shaped object, or receipt must not be confused with verified authority or successful execution.
