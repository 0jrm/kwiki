---
phase: 07-schema-and-migration-docs
plan: 01
subsystem: schema-and-migration-governance
provides: [canonical-v2-schema, migration-playbook, implementation-aligned-reference]
requires: [foundation-safety, graph-layer, lifecycle-layer, hybrid-retrieval, cross-cutting-intelligence, automation-collaboration]
affects: [release-readiness, onboarding, future-pr-evals]
---

# Phase 7 Plan 01: Canonical v2 Schema + Migration Summary

Shipped a documentation-only closeout for PR #15 by creating a single canonical v2 schema reference and wiring it into primary entrypoints.

## Accomplishments

- Created `.skills/llm-wiki-v2-schema/SCHEMA.md` as the implementation-faithful v2 reference
- Covered all required schema sections:
  - entity/relationship types and confidence semantics
  - frontmatter fields with additive defaults and backward-compat behavior
  - confidence + decay model and compatibility mapping
  - quality heuristic thresholds and lint behavior
  - contradiction/supersession semantics
  - `_graph/entities.jsonl` and `_graph/edges.jsonl` shapes
  - retrieval streams (BM25/vector/graph), RRF (`k=60`), fallback, and `--explain`
  - PII pattern classes and mode knobs
  - audit schema and operation taxonomy
  - hook event contracts
  - sync conflict classes and outcomes
- Added explicit migration guide in SCHEMA.md with:
  - preflight checklist
  - compatibility-first rollout order
  - minimum required vs optional upgrades
  - partial-adoption fallback behavior
  - validation checklist
  - rollback steps
- Added canonical-pointer references (without duplicating schema internals) in:
  - `README.md`
  - `AGENTS.md`
  - `CLAUDE.md`

## Files Created/Modified

- `.skills/llm-wiki-v2-schema/SCHEMA.md` (new)
- `.planning/phases/07-schema-and-migration-docs/07-01-SUMMARY.md` (new)
- `README.md` (schema pointer)
- `AGENTS.md` (schema pointer)
- `CLAUDE.md` (schema pointer)

## Decisions Made

- Treated summary artifacts from Phases 1-6 as authoritative for "implemented" statements.
- Marked uncertain/runtime-not-codified details as "not yet implemented" or "optional extension" to avoid overstating shipped behavior.
- Kept this phase documentation-only to preserve scope lock and avoid behavior drift.

## Issues Encountered

None.

## Phase 7 Complete

The v2 implementation now has a single canonical schema and migration reference aligned to shipped behavior, with top-level docs routed to that source to minimize future drift.
