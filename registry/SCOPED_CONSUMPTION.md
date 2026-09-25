# Scoped Consumption Contract

**Version:** 0.1

The Scoped Consumption Adapter is the final public-to-private boundary before Kernel integration.

```text
Source → Validator → Registry → Policy → Authorization → Consumption Envelope → Kernel
```

The adapter is fail-closed. It requires an explicit `ALLOW`, an authorized lifecycle state, `read` operation, policy revision, resource identity and a 64-character SHA-256 content digest.

The resulting envelope explicitly carries:

- source identity;
- resource identity;
- domain and resource type;
- policy revision;
- content digest;
- immutable envelope digest.

The envelope declares `mutation_allowed: false` and `execution_allowed: false`.

This layer does not commit anything to the Kernel. It produces a bounded input object that a separate Kernel-side consumer may accept or reject under its own trust rules.
