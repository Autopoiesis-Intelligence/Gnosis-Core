# Baseline Differential Audit

**Baseline:** `1a0e7afe2b612680aba0a4b7c159394e4657c3cd`
**Audit snapshot:** `8ad640797209e0278fb9b7b5c64e60fe061e387b`

## Result

The GitHub comparison shows that the audit snapshot contains exactly one commit after the packaging baseline: `8ad64079`, which only records CI runtime evidence and regression blockers. No Federation source or test files were introduced by that audit commit.

Therefore the observed 27 failures in the CI run recorded by `8ad64079` cannot be causally attributed to that audit commit itself.

The earlier Federation implementation commits precede the packaging baseline and require a separate comparison against the last known Core-green reference if one exists. This document deliberately does not classify those failures as pre-existing without that reference.

## Classification

- `8ad64079` audit commit → **not causal for the 27 failures**
- Federation implementation → **causal status not yet proven**
- Existing Core failures → **observed, attribution pending historical green baseline**

## Rule

No regression is declared introduced or pre-existing without a comparable test result from a commit that differs only in the relevant change set.
