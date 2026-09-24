# Core Recursive Stability Contract

## Objective
Prevent unbounded self-evolution, recursion and cascading failure from escaping governed execution.

## Required controls
Every recursive/evolutionary execution path MUST have:
- bounded work/step budget;
- explicit depth or cycle detection where recursion exists;
- deterministic failure/abort semantics;
- preserved failure evidence;
- recovery that cannot silently resurrect invalid authority.

A budget exhaustion is a controlled outcome, not an implementation success.

## Acceptance
Tests must cover cyclic transitions, repeated candidates, nested reflection, budget exhaustion, restart after abort and recovery from partial execution.

Status: DESIGNED / NOT_IMPLEMENTED.
