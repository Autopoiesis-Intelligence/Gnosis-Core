"""Recovery marker for canonical authority.py.

The canonical implementation is restored from the last valid authority commit
in Git history. This marker records the recovery target without introducing a
second authority module.
"""
CANONICAL_AUTHORITY_RECOVERY_COMMIT = "a5ff0f112f7d4442868a450b98e5946a02c850d6"
