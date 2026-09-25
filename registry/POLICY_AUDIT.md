# Policy and Authorization Audit Contract

**Version:** 0.1

Every authorization decision is reproducible from:

- request identity;
- source identity;
- policy identity;
- immutable policy revision;
- lifecycle state;
- domain;
- operation;
- resource type;
- update mode;
- decision reasons.

The policy engine emits `ALLOW` or `DENY` plus a deterministic SHA-256 decision digest.

## Trust boundary

The audit record proves what policy evaluation decided for the supplied inputs. It does not prove that the source content is true, that a human policy is legally sufficient, or that the Kernel must consume the result.

`DENY` is fail-closed. A policy revision must be explicit; no implicit current policy is allowed.
