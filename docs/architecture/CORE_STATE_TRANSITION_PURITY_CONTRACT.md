# Core State Transition Purity Contract

## Objective
Protect canonical state semantics from uncontrolled side effects and mutation bypasses.

## Rules
Core transition computation MUST be deterministic for identical inputs and explicit dependencies.
Canonical state MUST NOT be mutated through hidden globals, ambient process state, uncontrolled I/O, or direct external callbacks.
External effects MUST occur outside the pure transition boundary and return explicit results/evidence to the governed layer.
Every canonical mutation MUST converge on the protected transition/commit boundary.
Guard conditions MUST be explicit and testable.

## Recursive containment
Recursive or cascading evolution MUST have an explicit termination/budget condition and preserve failure evidence.

## Acceptance
Adversarial tests must cover hidden mutation, global-state dependence, direct state writes, external side effects during transition, guard bypass and recursive non-termination.

Status: DESIGNED / NOT_IMPLEMENTED.
