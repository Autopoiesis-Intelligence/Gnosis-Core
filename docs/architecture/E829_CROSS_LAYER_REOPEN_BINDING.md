# E8.29 — Cross-Layer Binding and Conflicting Replay After Reopen

Status: PARTIAL / UNVERIFIED.

After durable recovery, E8.29 reuses the recovered learning evidence and attempts cross-layer mutations.

Required fail-closed cases: provenance/result replay conflict and candidate/request mismatch.

No recovery path may weaken the admission/request/persistence bindings.

Acceptance requires exact runtime/CI evidence and full-chain execution.