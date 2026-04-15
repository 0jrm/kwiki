---
phase: 02-quality-and-graph-foundation
plan: 02
subsystem: quality-and-lint
provides: [quality-frontmatter, self-healing-lint, quality-heuristic]
requires:
  - phase: 01-foundation-and-safety
    provides: [confidence-fields, audit-full-coverage]
  - phase: 02-quality-and-graph-foundation
    provides: [entity-extract-skill, entities-frontmatter]
affects: [03-02, 05-01]
tech-stack:
  added: []
  patterns: [weighted-heuristic-scoring, self-healing-lint-with-report-escape-hatch, fuzzy-wikilink-resolution]
key-files:
  modified:
    - .skills/wiki-ingest/SKILL.md
    - .skills/wiki-update/SKILL.md
    - .skills/wiki-lint/SKILL.md
    - .skills/llm-wiki/SKILL.md
key-decisions:
  - "Quality heuristic: 7 weighted signals summing to 1.0, defined authoritatively in wiki-ingest Step 5a"
  - "Self-healing is the lint default; --report-only preserves pre-PR-#8 behavior for CI/audit use"
  - "Broken wikilinks resolved via 3-strategy ladder: fuzzy-within-category → graph alias → strip to plain text"
  - "Quality score is a signal, not a blocker: pages scoring < 0.4 are flagged but never auto-modified"
  - "Missing frontmatter remains report-only (schema completions are too lossy to auto-generate)"
---

# Phase 2 Plan 02: Quality Scoring + Self-Healing Lint Summary

**`quality:` frontmatter scored from 7 weighted signals on every write; wiki-lint auto-fixes orphans and broken wikilinks by default (with `--report-only` escape hatch).**

## Accomplishments
- 7-signal quality heuristic authoritatively defined in wiki-ingest Step 5a
- `quality:` field added to canonical template (llm-wiki), wiki-ingest, and wiki-update templates
- wiki-ingest Step 5a documents exact heuristic table with weights
- wiki-update Quality Scoring section references wiki-ingest Step 5a
- wiki-lint Operating Modes section: self-healing (default) vs `--report-only`
- wiki-lint orphans check: auto-add incoming links via cross-linker `--use-graph`
- wiki-lint broken-link check: 3-strategy resolution ladder (fuzzy → graph → strip)
- wiki-lint Step 2a: quality score recomputation check; drift > 0.1 triggers update
- Every auto-fix logged to `_meta/audit.jsonl`
- Fixed-Automatically report section added to output format
- `--report-only` flag preserves pre-PR-#8 behavior for CI
- llm-wiki quality field docs + lint behavior note in Reference

## Files Created/Modified
- `.skills/wiki-ingest/SKILL.md` — Step 5a heuristic table + quality: template/field docs/checklist
- `.skills/wiki-update/SKILL.md` — quality: template/Quality Scoring section/checklist
- `.skills/wiki-lint/SKILL.md` — Operating Modes + self-healing orphans/broken links + Step 2a + Fixed-Automatically report section + updated Quality Checklist
- `.skills/llm-wiki/SKILL.md` — canonical template quality: field + quality field docs + lint behavior note

## Decisions Made
[see key-decisions in frontmatter above]

## Issues Encountered
None.

## Next Step
Phase 2 complete — MVP-5 subset done. Ready for `/gsd:complete-milestone` or proceed to Phase 3 (Lifecycle Layer).
