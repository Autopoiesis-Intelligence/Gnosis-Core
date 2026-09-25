# Authorization Scope Contract

**Version:** 0.1

Authorization is scoped. A registry source never receives implicit global permission to influence the private Kernel.

An authorization request is evaluated against four explicit dimensions:

- `domain`
- `operation`
- `resource_type`
- `update_mode`

The source must also be in `authorized`, `verified` or `active` lifecycle state and the request must reference a policy revision.

## Example scope

```yaml
domains:
  - mathematics
operations:
  - read
resource_types:
  - research_record
update_modes:
  - pull
```

This means a mathematics source may be consumed only for the declared resource and operation. It does not authorize arbitrary execution, mutation of the source, or direct Kernel state changes.

`DENY` is the fail-closed result for any scope mismatch.
