# R3.2 — Persisted Learning Influence Proof

## Claim

An admitted verification failure can cross the persistence boundary and seed the next learning cycle after restart.

## Proof boundary

This test currently proves the contract-level handoff:

Cycle N failure → admitted counterexample → persisted evidence object → reconstructed admission → Cycle N+1 input.

It does not claim that the current GitHub process or production persistence backend has been exercised by a real process crash.

## Required runtime proof

1. persist through the actual configured persistence backend;
2. terminate the process;
3. restart;
4. recover the exact evidence;
5. create the next cycle from recovered evidence;
6. compare against a no-evidence control;
7. verify no authority escalation occurred.

Until those steps pass, R3.2 remains PARTIAL.
