---
phase: 01-foundation-and-safety
plan: 01
subsystem: frontmatter-schema
provides: [confidence-fields]
affects: [02-01, 03-01, 03-02, 03-03, 05-01, 05-02]
tech-stack:
  added: []
  patterns: [confidence-frontmatter, decay-rate-enum]
key-files:
  - .skills/wiki-ingest/SKILL.md
  - .skills/wiki-update/SKILL.md
  - .skills/llm-wiki/SKILL.md
key-decisions:
  - "confidence default 0.5 for ingest, 0.8 for wiki-update project pages"
  - "decay_rate enum: low|medium|high (not numeric — readable at a glance)"
  - "last_confirmed = ingest timestamp on create; no retroactive backfill"
---

# Phase 1 Plan 01: Confidence Frontmatter Summary

**Added confidence/provenance frontmatter fields (confidence, sources_count, last_confirmed, decay_rate) to wiki-ingest, wiki-update, and llm-wiki canonical template.**

## Accomplishments

- Four new frontmatter fields added to page template across all three primary SKILL.md files
- llm-wiki canonical template updated as the authoritative spec with a reference table documenting all four fields
- Field instructions added to wiki-ingest Step 5 with worked example and update rules
- wiki-update Step 4 template and new Quality Checklist updated
- Backward compat preserved — no retroactive vault rewrites

## Files Created/Modified

- `.skills/wiki-ingest/SKILL.md` — confidence field instructions + example after provenance section; checklist item added
- `.skills/wiki-update/SKILL.md` — frontmatter template + confidence instructions + Quality Checklist added
- `.skills/llm-wiki/SKILL.md` — canonical template + reference table added before provenance summary section

## Decisions Made

- confidence default 0.5 for ingest (neutral), 0.8 for wiki-update (live codebase = high confidence)
- decay_rate uses string enum not float — more readable in vault inspection
- last_confirmed set to ingest time on create; no retroactive backfill
- Fields placed after provenance block, before created — logical grouping with other epistemic metadata

## Issues Encountered

None.

## Next Step

Ready for 01-02-PLAN.md (PII filter)
