"""Compatibility exports for the trusted owner-authority issuer.

The implementation lives in authority.py so the authority dependency graph remains acyclic.
"""
from __future__ import annotations

from gnosis.reflection.authority import TrustedIssuerInput, TrustedOwnerIssuer

__all__ = ["TrustedIssuerInput", "TrustedOwnerIssuer"]
