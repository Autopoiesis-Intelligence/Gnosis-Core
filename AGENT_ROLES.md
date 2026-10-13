# Gnosis-Core — AI Agent Roles and Authority

## Current operating model

ChatGPT is the active implementation, integration, and audit assistant for the current project workflow. Other AI services are not assumed to be active participants or independent reviewers unless the project owner explicitly reactivates them for a specific task.

Access to repository data is not the same as authority to change protected state. A tool connection, generated patch, test result, or recommendation does not independently grant execution authority.

## Responsibilities

### ChatGPT — implementation, integration, and audit

- inspect current repository state before acting;
- make bounded code and documentation changes within the user's granted scope;
- run or inspect available tests and CI;
- distinguish implementation from reachability, runtime behavior, persistence, audit, and CI proof;
- record exact commits, failures, unresolved questions, and next steps;
- never certify a change solely from its own narrative or a synthetic test.

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
