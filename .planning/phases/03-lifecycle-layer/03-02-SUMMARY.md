---
phase: 03-lifecycle-layer
plan: 02
subsystem: retention-decay
provides: [decayed-confidence, stale-page-detection, reconfirm-flow]
requires: [confidence-fields, quality-heuristic]
affects: [03-03, 05-01]
tech-stack:
  added: [python-helper, pytest-unit-tests]
  patterns: [exponential-confidence-decay, read-time-normalization, reconfirm-branching]
key-files:
  modified:
    - .skills/wiki-lint/SKILL.md
    - .skills/wiki-ingest/SKILL.md
    - .skills/llm-wiki/SKILL.md
    - README.md
  added:
    - .skills/wiki-lint/_lib/decay.py
    - .skills/wiki-lint/_lib/test_decay.py
key-decisions:
  - "Decay equation fixed: decayed = base_confidence * exp(-k * days_since_last_confirmed)"
  - "Rate mapping: slow=0.0015, medium=0.005, fast=0.02"
  - "Compatibility aliases supported at read time: low->slow, high->fast"
  - "Decay is derived signal only; lint never overwrites base confidence"
  - "--reconfirm path branches into re-ingest or archive outcomes"
---

# Phase 3 Plan 02: Retention Decay Summary

Retention decay is now first-class: stale confidence is derived at read-time and can trigger reconfirm/archive decisions without mutating base confidence metadata.

## Accomplishments
- Added reusable decay helper in `.skills/wiki-lint/_lib/decay.py`
- Added deterministic unit tests in `.skills/wiki-lint/_lib/test_decay.py` (rates, aliases, bounds, now injection)
- Added `Decayed below threshold` reporting section (`decayed < 0.25`) in `wiki-lint`
- Documented `--reconfirm` flow with explicit re-ingest vs archive outcomes
- Aligned ingest/canonical docs + README around `slow|medium|fast` plus compatibility mapping and half-life guidance

## Files Created/Modified
- `.skills/wiki-lint/_lib/decay.py` — decay math + enum normalization + guards
- `.skills/wiki-lint/_lib/test_decay.py` — focused unit coverage for helper
- `.skills/wiki-lint/SKILL.md` — retention-decay, reporting, reconfirm mode docs
- `.skills/wiki-ingest/SKILL.md` — base confidence vs decayed-confidence semantics
- `.skills/llm-wiki/SKILL.md` — canonical field semantics and decay behavior
- `README.md` — lifecycle semantics + decay half-life table

## Issues Encountered
None.

## Next Step
Proceed with consolidation tier model in `03-03`.
