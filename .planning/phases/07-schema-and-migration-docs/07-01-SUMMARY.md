---
phase: 07-schema-and-migration-docs
plan: 01
subsystem: schema-and-migration-governance
provides: [canonical-v2-schema, migration-playbook, implementation-aligned-reference]
requires: [foundation-safety, graph-layer, lifecycle-layer, hybrid-retrieval, cross-cutting-intelligence, automation-collaboration]
affects: [release-readiness, onboarding, future-pr-evals]
tech-stack:
  added: []
  patterns: [single-source-of-truth-schema, compatibility-first-migration, additive-field-design]
key-files:
  created:
    - .skills/llm-wiki-v2-schema/SCHEMA.md
    - .skills/llm-wiki-v2-schema/SKILL.md
  modified:
    - README.md
    - AGENTS.md
    - CLAUDE.md
    - .cursor/rules/obsidian-wiki.mdc
key-decisions:
  - "SCHEMA.md is the single canonical v2 reference; bootstrap docs link to it without duplicating detail"
  - "Migration is compatibility-first: v2 fields are additive, old pages remain readable, missing artifacts degrade gracefully"
  - "Implementation-aligned: only shipped behavior is documented as implemented; aspirational items are marked as optional extensions"
---

# Phase 7 Plan 01: Schema + Migration Docs Summary

Canonical v2 schema document and migration guide shipped as the definitive reference for every frontmatter field, graph format, audit schema, retrieval fusion, hook contract, sync semantic, and upgrade path.

## Accomplishments
- Created `.skills/llm-wiki-v2-schema/SCHEMA.md` covering all v2 subsystems: entity types, relationship types, frontmatter spec (base + v2 additive fields), confidence/decay model, quality thresholds, contradiction/supersession semantics, graph storage schema, retrieval schema (BM25 + graph + optional vector with RRF), PII patterns, audit log schema, hook event contracts, and sync conflict classes
- Added migration guide with preflight checklist, compatibility-first rollout order, minimum required changes vs optional enhancements, per-feature partial-adoption fallback behavior, validation checklist, and rollback guidance
- Wired schema references into README.md, AGENTS.md, CLAUDE.md, and .cursor/rules
- Updated skill routing tables across all bootstrap docs to include v2 skills (entity-extract, wiki-crystallize, wiki-sync, _hooks, llm-wiki-v2-schema)
- Updated vault structure diagrams to reflect v2 additions (_graph/, _archive/, audit.jsonl)

## Files Created/Modified
- `.skills/llm-wiki-v2-schema/SCHEMA.md` — canonical v2 schema + migration guide
- `.skills/llm-wiki-v2-schema/SKILL.md` — agent routing descriptor
- `README.md` — v2 schema reference pointer (already present from Phase 6)
- `AGENTS.md` — updated skill routing, vault structure, schema reference
- `CLAUDE.md` — updated skill routing, vault structure, schema reference
- `.cursor/rules/obsidian-wiki.mdc` — updated skill routing, schema reference

## Issues Encountered
None.

## Next Step
All 7 phases complete. Next: dogfooding on real vault, upstream coordination with @Ar9av/obsidian-wiki.
