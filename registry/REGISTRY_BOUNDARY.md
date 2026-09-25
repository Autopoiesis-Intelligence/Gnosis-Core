# Registry Trust Boundary

The Registry is the policy boundary between public Memory Sources and private Kernel consumption.

```text
Public Source
   ↓
Validator
   ↓
Registry Record
   ↓
Policy / Authorization
   ↓
Scoped Consumption
   ↓
Private Kernel
```

The Registry must retain the source identity, immutable registration revision, validator version, policy revision, provenance root, lifecycle state and authorization scope.

No registry record may grant unrestricted influence over the Kernel. Consumption must remain scoped and auditable.
