# E7.108 Execution Record Acceptance Matrix

Status: evidence gate, not an execution authorization.

A record is acceptable only when:
- batch identity is present;
- exact target commit is present;
- repository ref and environment identity are recorded;
- candidate selection and baseline are frozen;
- commands are recorded;
- evidence policy and verification matrix revisions are recorded;
- every criterion has expected, observed, pass/fail and evidence_id;
- terminal state is explicit;
- incomplete or missing criterion evidence cannot be accepted;
- FAILED or INTERRUPTED is never promoted to success.

This matrix does not grant execution authority and does not authorize Core mutation.
