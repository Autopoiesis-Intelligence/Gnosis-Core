"""Canonical evidence contracts shared across Core-facing verification and Research Machine.

This package contains identity, provenance, and audit contracts only.
Experimental evolution machinery must not be required by canonical evidence consumers.
"""
from .provenance import *
from .audit import *
