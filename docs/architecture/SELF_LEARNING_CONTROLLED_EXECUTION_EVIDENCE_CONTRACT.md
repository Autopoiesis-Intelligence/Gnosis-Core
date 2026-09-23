# E7.48 — Controlled Execution Evidence / Mutation Receipt

## Objective
Record the externally authorized result of an execution plan without allowing the evidence layer to execute the mutation.

## Boundary
This module records evidence only. It MUST NOT execute commands, mutate contracts/Core, grant authority, or infer authorization.

## Receipt fields
Each receipt records:
- receipt_id;
- plan_id;
- review_id;
- proposal_id;
- result;
- target;
- before_digest;
- after_digest;
- executor;
- authorization_reference;
- created_at;
- provenance;
- authority.

Allowed results:
APPLIED, REJECTED, FAILED, NOOP_REJECTED.

An APPLIED receipt MUST demonstrate a changed target digest.

## Provenance
Receipt identity is deterministic for fixed inputs. Receipt collections have a deterministic digest.

## Privacy
Evidence stores references/digests, not private user or partner payloads.

## Status
IMPLEMENTED / UNVERIFIED.
