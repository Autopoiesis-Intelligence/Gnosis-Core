# Source Validator — Rights and License Layer

**Version:** 0.7

The validator now checks the license declaration in `SOURCE.yaml`.

## Checks

- a non-empty `license` value is required by the manifest;
- a missing `LICENSE` file produces a warning;
- recognized standard license identifiers are accepted;
- proprietary, custom, unknown or unrecognized markers are surfaced as warnings rather than silently treated as open-source rights.

Warnings do not assert legal compatibility. They identify metadata that requires explicit policy or human/legal review before federation use.

A validator PASS still does not grant Genezis ownership, redistribution rights, sublicensing rights or permission to expose private material.
