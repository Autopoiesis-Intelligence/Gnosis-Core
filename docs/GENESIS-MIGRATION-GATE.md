# Genesis Migration Gate

A Genesis module may move toward the new architecture only when all gates pass:

1. **Responsibility** — the module has one clearly identified architectural layer.
2. **Dependency direction** — dependencies point toward lower-level contracts; no Core back-dependency.
3. **Trust** — the module does not silently acquire trusted-state authority.
4. **Data boundary** — private, research, user, and commercial data are explicitly separated.
5. **Context** — context continuity is exposed through a contract, not by copying private runtime memory.
6. **Evidence** — existing tests/audit/provenance evidence are mapped to the migrated behavior.
7. **Replacement** — the old implementation remains available until the new implementation has equivalent evidence.
8. **Rollback** — migration can be reverted without losing provenance or historical evidence.

## Decisions

- KEEP: private Genesis orchestration and proprietary evolution mechanisms.
- EXTRACT: minimal contracts needed by Core/Product.
- MOVE: reusable public interfaces and sanitized knowledge/evidence.
- REWRITE: modules whose current boundaries mix trust, persistence, context, and orchestration.
- ARCHIVE: historical implementation/evidence that is no longer part of runtime.

No module is considered migrated merely because its files were copied.
