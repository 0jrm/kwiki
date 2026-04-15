---
name: on_session_end
description: >
  Session-boundary wrap-up hook for wiki workflows. Captures end-of-session
  signals and suggests crystallization/backlog follow-ups. Additive and opt-in;
  primary workflow behavior is unchanged when not invoked.
---

# Hook: on_session_end

Use this hook at workflow completion to make closure behavior explicit and repeatable.

## Trigger Contract

- **when**: A write-oriented wiki workflow finishes successfully.
- **inputs**:
  - `vault_path` (required)
  - `session_goal` (optional)
  - `pages_touched` (optional list)
  - `suggest_crystallization` (`true` | `false`, optional; default `true`)
- **expected side effects**:
  - Optional wrap-up notes in `log.md`
  - Optional suggestion output for `wiki-crystallize`
  - Append-only audit entry only when this hook writes

## Default Actions (safe baseline)

1. Summarize pages and operations touched in this workflow.
2. Identify unresolved items:
   - contradiction review items
   - ambiguous claims requiring confirmation
   - low-quality pages queued for cleanup
3. Suggest a crystallization target if the session generated enough new material.

## Optional Actions

- Append one `SESSION_END` line to `log.md` with counts and outcome.
- Create/append a lightweight backlog checkpoint note (non-destructive) when explicitly requested.

## Idempotency Guidance

- `on_session_end` should produce at most one wrap-up write per session key.
- If called again with identical `(session_goal, pages_touched hash, date-hour)`, return previous summary and avoid duplicate writes.

## Safety Rules

- Never archive, rebuild, or delete content from this hook.
- Suggestions are advisory; user approval is required for any follow-up operation with side effects.
- Hook failures must be fail-soft and must not invalidate already-completed primary writes.

## Audit Expectations

- If `log.md` or backlog notes are written, append one `_meta/audit.jsonl` entry after the write.
- Read-only summarization does not require audit logging.

## worked example

Trigger payload:

```json
{
  "event": "session_end",
  "vault_path": "/vault",
  "session_goal": "sync kwiki project learnings",
  "pages_touched": [
    "projects/kwiki/kwiki.md",
    "concepts/event-hooks.md"
  ],
  "suggest_crystallization": true
}
```

Ordered action sequence:
1. Aggregate touched pages and unresolved conflict markers
2. Suggest: "Run `wiki-crystallize` on this session"
3. Append one line to `/vault/log.md`:
   `- [2026-04-15T11:40:00Z] SESSION_END goal="sync kwiki project learnings" pages_touched=2 unresolved=1`
4. Append one audit line to `/vault/_meta/audit.jsonl`

Expected bookkeeping updates:
- `index.md`: unchanged
- `log.md`: +1 `SESSION_END` line
- `.manifest.json`: unchanged
- `_meta/audit.jsonl`: +1 append-only entry
