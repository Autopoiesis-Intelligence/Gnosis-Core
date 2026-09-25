# Source Validator — Integrity Layer

**Version:** 0.6

The validator now verifies configured content digests from provenance records.

A provenance record may declare `content_path` and `content_sha256`. The validator reads the referenced local file, computes SHA-256, and fails closed when the digest differs or the target is missing.

This binds provenance to actual repository content rather than merely checking that a digest string has the correct shape.

The validator remains offline and does not trust branch names, remote services, Registry credentials or the private Kernel.

A digest match proves content identity for the checked bytes; it does not prove the truth or quality of the content.
