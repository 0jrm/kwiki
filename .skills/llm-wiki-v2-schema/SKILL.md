---
name: llm-wiki-v2-schema
description: >
  Canonical v2 schema reference and migration guide. Read this when the user asks about the v2 data model,
  frontmatter field specifications, graph storage format, confidence/decay rules, quality thresholds,
  audit log schema, hook contracts, sync conflict classes, or how to migrate an existing v1 vault to v2.
  This is the single source of truth for everything built in Phases 1-6.
---

# LLM Wiki v2 Schema — Reference Skill

This skill points to the canonical v2 schema document. Read `SCHEMA.md` in this directory for the full specification.

## When to Use

- User asks about v2 frontmatter fields, defaults, or compatibility behavior
- User asks about entity types, relationship types, or `_graph/` format
- User asks about confidence, decay, quality scoring, or consolidation tiers
- User asks about the audit log, PII patterns, or hook contracts
- User asks about sync conflict classes or mesh reconciliation semantics
- User wants to migrate an existing vault from v1 to v2
- Another skill needs to look up the canonical field spec

## The Document

Read `SCHEMA.md` in this same directory. It covers:

1. Entity types and relationship types (with ID formats and confidence ladder)
2. Frontmatter spec (required base fields + v2 additive fields with defaults)
3. Confidence rules and decay constants (Ebbinghaus model, compatibility mappings)
4. Quality threshold (seven-signal model, lint thresholds)
5. Contradiction and supersession semantics (write preflight classes, resolution policy)
6. Graph storage schema (`_graph/entities.jsonl`, `_graph/edges.jsonl`)
7. Retrieval schema (BM25 + graph + optional vector, RRF fusion)
8. PII patterns and mode knobs
9. Audit log schema (`_meta/audit.jsonl`)
10. Hook event contracts (`on_session_start`, `on_new_source`, `on_session_end`)
11. Sync conflict classes and outcomes
12. Migration guide (preflight, rollout order, validation, rollback)
13. Known gaps and future extensions
