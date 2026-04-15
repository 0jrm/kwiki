---
phase: 05-cross-cutting-intelligence
plan: 02
subsystem: crystallization-layer
provides: [session-digest-distillation, lifecycle-aware-promotion, contradiction-aware-compaction]
requires: [write-time-contradiction-detection, confidence-fields, typed-graph-jsonl]
affects: [06-01, 07-01]
tech-stack:
  added: []
  patterns: [thread-to-digest-distillation, tier-aware-output-selection, provenance-preserving-promotion]
key-files:
  modified:
    - .skills/wiki-crystallize/SKILL.md
    - .skills/llm-wiki/SKILL.md
    - README.md
key-decisions:
  - "Crystallization defaults to episodic output and escalates to semantic/procedural only with enough reinforcing evidence"
  - "Digest structure always includes contradictions and open questions to avoid false certainty"
  - "Crystallized outputs follow existing frontmatter lifecycle fields for compatibility"
  - "Crystallization writes full bookkeeping signals: index, log, manifest, and audit"
  - "Lower-tier provenance is preserved on promotion; no destructive merge"
---

# Phase 5 Plan 02: Crystallization Skill Summary

`wiki-crystallize` is now defined as a first-class skill for distilling sessions/threads into structured, lifecycle-aware digest pages.

## Accomplishments
- Added new `.skills/wiki-crystallize/SKILL.md` with end-to-end flow: gather -> scan contradictions -> structure digest -> promote -> integrate -> bookkeep
- Added lifecycle-aware output modes (episodic default, semantic, procedural) and promotion rules aligned with Phase 3
- Included required frontmatter + section template for consistent digest artifacts
- Included contradiction-aware handling inside crystallization flow to prevent silent conflict collapse
- Updated canonical (`llm-wiki`) and user-facing (`README`) docs to include the new skill

## Files Created/Modified
- `.skills/wiki-crystallize/SKILL.md` — new crystallization operational skill
- `.skills/llm-wiki/SKILL.md` — companion-skill reference and lifecycle alignment
- `README.md` — feature note, skills table row, and project structure entry

## Issues Encountered
None.

## Next Step
Phase 5 complete; proceed to Phase 6 (`06-01`) event hooks.
