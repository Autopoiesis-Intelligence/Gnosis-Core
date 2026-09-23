# Partner Contract Generation Log

Machine-maintained append-only intent log for generated candidate contracts.

Each entry SHOULD contain:
- contract_id
- source references/revisions
- generator context
- scope
- generated revision
- status
- validation requirements
- timestamp/commit evidence when persisted by an execution layer

This log is an evidence/index layer, not an authority root.
