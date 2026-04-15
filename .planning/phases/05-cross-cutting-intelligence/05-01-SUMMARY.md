---
phase: 05-cross-cutting-intelligence
plan: 01
subsystem: write-time-contradiction-detection
provides: [cross-page-conflict-preflight, deterministic-resolution-strategy, ambiguity-preservation]
requires: [confidence-fields, supersession-chain, typed-graph-jsonl]
affects: [05-02, 06-02]
tech-stack:
  added: []
  patterns: [conflict-preflight, classify-before-write, explicit-resolution-policy]
key-files:
  modified:
    - .skills/wiki-ingest/SKILL.md
    - .skills/llm-wiki/SKILL.md
    - README.md
key-decisions:
  - "Contradiction detection runs as a write preflight, not as an afterthought during merge"
  - "Conflicts are classified as no_conflict/possible_conflict/conflict to separate uncertainty from hard contradiction"
  - "Possible conflicts preserve both claims with ^[ambiguous] and require review notes"
  - "Hard conflicts resolve through existing supersession mechanics; silent overwrite is disallowed"
  - "Behavior is additive and backward compatible for legacy pages without graph/frontmatter upgrades"
---

# Phase 5 Plan 01: Contradiction Detection on Write Summary

`wiki-ingest` now includes a cross-page contradiction preflight that forces explicit conflict resolution before writes.

## Accomplishments
- Added contradiction preflight step in `wiki-ingest` covering candidate selection, claim comparison, and resolution planning
- Added explicit conflict classes (`no_conflict`, `possible_conflict`, `conflict`) and mapped each class to deterministic handling
- Added explicit no-silent-overwrite rule for conflicting claims
- Aligned `llm-wiki` canonical docs with write-time contradiction handling across ingest/crystallization paths
- Updated README feature list to expose contradiction-aware write behavior

## Files Created/Modified
- `.skills/wiki-ingest/SKILL.md` — contradiction preflight workflow and checklist updates
- `.skills/llm-wiki/SKILL.md` — lifecycle guidance for contradiction-aware write paths
- `README.md` — user-facing capability note

## Issues Encountered
None.

## Next Step
Proceed to `05-02` to add the `wiki-crystallize` skill for structured session/thread distillation.
