---
phase: 06-automation-and-collaboration
plan: 01
subsystem: event-hooks-automation
provides: [session-boundary-triggers, ingest-boundary-triggers, fail-soft-hook-orchestration]
requires: [audit-log, confidence-fields, crystallization-layer]
affects: [06-02, 07-01]
tech-stack:
  added: []
  patterns: [trigger-contracts, opt-in-automation, fail-soft-execution]
key-files:
  modified:
    - .skills/_hooks/on_session_start/SKILL.md
    - .skills/_hooks/on_session_end/SKILL.md
    - .skills/_hooks/on_new_source/SKILL.md
    - .skills/wiki-ingest/SKILL.md
    - .skills/wiki-update/SKILL.md
    - .skills/llm-wiki/SKILL.md
    - README.md
key-decisions:
  - "Hooks are explicit and opt-in; workflows remain unchanged when hooks are not invoked"
  - "on_new_source fires once per source unit after primary bookkeeping, never per chunk"
  - "Hook failures are fail-soft and cannot invalidate successful primary writes"
  - "Hook side-effect writes require append-only audit visibility"
  - "Hooks may suggest follow-up actions but cannot perform destructive operations silently"
---

# Phase 6 Plan 01: Event Hooks Summary

Event hooks are now first-class automation primitives with deterministic trigger contracts and additive behavior.

## Accomplishments
- Added three new hook skills under `.skills/_hooks/` (`on_session_start`, `on_new_source`, `on_session_end`) with trigger/input/side-effect contracts
- Added idempotency, audit expectations, and worked examples in each hook file
- Wired `wiki-ingest` to call `on_new_source` after successful source writes and bookkeeping
- Wired `wiki-update` to call `on_session_start` at workflow start and `on_session_end` at completion
- Updated canonical and user-facing docs (`llm-wiki`, `README`) to document hooks as an additive automation layer

## Files Created/Modified
- `.skills/_hooks/on_session_start/SKILL.md` — new session preflight hook
- `.skills/_hooks/on_session_end/SKILL.md` — new session wrap-up hook
- `.skills/_hooks/on_new_source/SKILL.md` — new ingest-boundary normalization hook
- `.skills/wiki-ingest/SKILL.md` — explicit hook invocation timing + fail-soft guidance
- `.skills/wiki-update/SKILL.md` — explicit start/end hook invocation + fail-soft guidance
- `.skills/llm-wiki/SKILL.md` — canonical hook layer semantics
- `README.md` — feature note + skills table entries for hooks

## Issues Encountered
None.

## Next Step
Proceed to `06-02` to add `wiki-sync` and deterministic multi-agent reconciliation semantics.
