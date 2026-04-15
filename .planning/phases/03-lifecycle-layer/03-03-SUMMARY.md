---
phase: 03-lifecycle-layer
plan: 03
subsystem: consolidation-tiers
provides: [tier-metadata, promotion-rules, tier-health-audits]
requires: [supersession-history, retention-decay]
affects: [05-02, 07-01]
tech-stack:
  added: []
  patterns: [evidence-driven-promotion, provenance-preserving-consolidation, tier-health-audits]
key-files:
  modified:
    - .skills/wiki-ingest/SKILL.md
    - .skills/wiki-lint/SKILL.md
    - .skills/llm-wiki/SKILL.md
    - README.md
key-decisions:
  - "Tier taxonomy fixed to working -> episodic -> semantic -> procedural"
  - "Promotion thresholds are explicit and evidence-count based"
  - "Promotions compile/copy upward and preserve source-tier provenance"
  - "wiki-lint reports tier drift, promotion opportunities, and provenance gaps without auto-promotion"
  - "README documents lifecycle semantics and notes future wiki-crystallize targeting episodic/semantic tiers"
---

# Phase 3 Plan 03: Consolidation Tiers Summary

Lifecycle tiers are now explicit metadata and process: content can promote by evidence while retaining lower-tier provenance.

## Accomplishments
- Added tier metadata (`tier`, `promoted_from`, `promotion_evidence_count`) to ingest guidance and templates
- Added promotion evaluation workflow and threshold rules in `wiki-ingest`
- Added `Tier Drift`, `Promotion Opportunities`, and `Provenance Gaps` checks in `wiki-lint`
- Added canonical tier model + promotion rules in `llm-wiki`
- Added README lifecycle section and future `wiki-crystallize` target note

## Files Created/Modified
- `.skills/wiki-ingest/SKILL.md` — tier fields + promotion workflow + lifecycle checklist
- `.skills/wiki-lint/SKILL.md` — tier health and promotion-readiness reporting
- `.skills/llm-wiki/SKILL.md` — canonical tier model and thresholds
- `README.md` — user-facing lifecycle semantics documentation

## Issues Encountered
None.

## Next Step
Phase 3 complete; proceed to Phase 4 (`04-01`) graph traversal + hybrid search.
