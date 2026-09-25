# INTERFACE-RUNNER-01

Status: SPECIFICATION
Version: 1.0

## Inputs
- contract_id
- contract_version
- core_revision
- fixture_id

## Execution
1. Load immutable contract.
2. Validate dependencies and preconditions.
3. Execute the selected fixture against the declared Core revision.
4. Observe only permitted evidence surfaces.
5. Evaluate invariants and expected negative behavior.
6. Emit an execution record.

## Prohibitions
- No Core mutation authority.
- No contract modification.
- No silent Core revision substitution.
- No automatic repair.

## Results
PASS | FAIL | BLOCKED | NOT_IMPLEMENTED

A PASS is valid only when all mandatory evidence requirements are satisfied.