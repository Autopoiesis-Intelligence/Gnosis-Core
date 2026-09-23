# E7.43A — Continuously Updated Current Partner Contract Block

## Purpose

Maintain one generated partner-facing block containing the current contract index for partnership integration.

This is NOT a proof-of-learning artifact.

It is the continuously refreshed contract-information surface requested for partners.

## Source of truth

The partner contract registry and individual contract artifacts remain authoritative for contract content. The generated block is a synchronized index/briefing surface.

## Update mechanism

Generator:
scripts/update_partner_contract_block.py

Output:
docs/partners/CURRENT_PARTNER_CONTRACT_BLOCK.md

Automatic refresh:
.github/workflows/refresh-partner-contract-block.yml
hourly schedule plus manual dispatch

The generator records generation time, source revision and a deterministic index digest.

## Boundary

The block MUST NOT:
- grant partner permissions;
- represent governance acceptance;
- expose private user/partner payloads;
- replace contract artifacts;
- replace Ψ-Core;
- imply that a generated index is executable authority.

## Partner use

A partner can consume this block as the current contract map before receiving or integrating with the appropriate governed interfaces.

## Status

IMPLEMENTED / UNVERIFIED.
