---
phase: 06-automation-and-collaboration
plan: 02
subsystem: mesh-sync-collaboration
provides: [multi-agent-state-reconciliation, conflict-classification, audited-sync-outcomes]
requires: [event-hooks-automation, audit-log, typed-graph-jsonl, write-time-contradiction-detection]
affects: [07-01]
tech-stack:
  added: []
  patterns: [class-based-conflicts, preserve-local-writes, review-queue-escalation]
key-files:
  modified:
    - .skills/wiki-sync/SKILL.md
    - .skills/wiki-update/SKILL.md
    - .skills/wiki-ingest/SKILL.md
    - .skills/wiki-rebuild/SKILL.md
    - .skills/llm-wiki/SKILL.md
    - README.md
key-decisions:
  - "Sync uses four canonical conflict classes with deterministic handling"
  - "Only safe classes auto-merge; claim/structural conflicts escalate to explicit review"
  - "Every sync attempt is auditable with outcome and conflict-count metadata"
  - "Local writes are preserved by default when reconciliation is unresolved"
  - "Single-agent workflows remain unchanged when wiki-sync is not invoked"
---

# Phase 6 Plan 02: Mesh Sync Summary

`wiki-sync` is now defined as the collaboration-layer primitive for deterministic, non-destructive reconciliation across concurrent wiki edits.

## Accomplishments
- Added new `.skills/wiki-sync/SKILL.md` with snapshot comparison, conflict classification, safe auto-merge, and review queue escalation flow
- Defined the four-class conflict model (`non_overlapping`, `same_page_non_overlapping_sections`, `same_claim_conflict`, `structural_conflict`)
- Added explicit audit requirements for sync outcomes (`merged`, `requires_review`, `aborted`) with conflict counts
- Added `wiki-sync` touchpoints to write-path skills:
  - `wiki-update`: preflight + post-write reconciliation
  - `wiki-ingest`: collaboration preflight before large batches
  - `wiki-rebuild`: post-rebuild sync checkpoint
- Updated canonical/user-facing docs to include collaboration semantics and backward compatibility guarantees

## Files Created/Modified
- `.skills/wiki-sync/SKILL.md` — new reconciliation skill
- `.skills/wiki-update/SKILL.md` — sync touchpoints and local-write safety rules
- `.skills/wiki-ingest/SKILL.md` — collaborative preflight guidance
- `.skills/wiki-rebuild/SKILL.md` — post-rebuild sync guidance
- `.skills/llm-wiki/SKILL.md` — mesh sync semantics and conflict classes
- `README.md` — feature note and skill table/project structure entries for wiki-sync

## Issues Encountered
None.

## Next Step
Phase 6 complete; proceed to `07-01` for canonical v2 schema + migration documentation.
