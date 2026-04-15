---
phase: 03-lifecycle-layer
plan: 01
subsystem: supersession-chain
provides: [supersession-history, ambiguity-marking, volatility-reporting]
requires:
  - phase: 01-foundation-and-safety
    provides: [confidence-fields]
affects: [03-02, 03-03, 05-01]
tech-stack:
  added: []
  patterns: [contradiction-based-supersession, ambiguity-guardrails, non-destructive-claim-history]
key-files:
  modified:
    - .skills/wiki-ingest/SKILL.md
    - .skills/wiki-lint/SKILL.md
    - .skills/llm-wiki/SKILL.md
key-decisions:
  - "Contradiction defined as same entity+attribute with different asserted value"
  - "Confidence delta < 0.2 is ambiguous: retain both claims and mark ^[ambiguous]"
  - "True contradiction moves prior claim to ## Superseded with superseded_on, superseded_by_source, previous_confidence"
  - "supersession_count increments only on true supersession"
  - "Backward compatibility preserved: legacy pages without supersession metadata remain valid"
---

# Phase 3 Plan 01: Supersession + Version Chain Summary

Contradictory updates now preserve epistemic history through `## Superseded` instead of silently overwriting prior claims.

## Accomplishments
- Added contradiction resolution flow to `wiki-ingest` with ambiguity guard (`abs(delta_confidence) < 0.2`)
- Added required supersession annotations (`superseded_on`, `superseded_by_source`, `previous_confidence`)
- Added `supersession_count` guidance and update rules (increment only on true supersession)
- Added supersession volatility reporting + ambiguity backlog checks to `wiki-lint`
- Updated canonical `llm-wiki` docs with `## Superseded` pattern and worked before/after example

## Files Created/Modified
- `.skills/wiki-ingest/SKILL.md` — contradiction/supersession workflow + checklist updates
- `.skills/wiki-lint/SKILL.md` — supersession hotspot + ambiguity accumulation reporting
- `.skills/llm-wiki/SKILL.md` — canonical supersession metadata and examples

## Issues Encountered
None.

## Next Step
Proceed with retention decay implementation in `03-02`.
