---
name: on_session_start
description: >
  Session-boundary preflight hook for wiki workflows. Runs lightweight health and
  backlog checks at the beginning of a wiki session. This hook is additive and
  optional: primary workflow behavior is unchanged when it is not invoked.
---

# Hook: on_session_start

Use this hook as an explicit, opt-in automation primitive at the beginning of a wiki workflow (for example, at the start of `wiki-update` in collaborative mode).

## Trigger Contract

- **when**: A write-oriented session starts (project sync, batch ingest, or maintenance run).
- **inputs**:
  - `vault_path` (required)
  - `session_goal` (optional text)
  - `collaboration_mode` (`single-agent` | `multi-agent`, optional)
  - `status_snapshot` (`true` | `false`, optional; default `false`)
- **expected side effects**:
  - Read-only checks by default
  - Optional append-only bookkeeping to `log.md` and `_meta/audit.jsonl` when a status snapshot is requested
  - No destructive operations

## Default Actions (safe baseline)

1. Confirm required control files exist: `index.md`, `log.md`, `.manifest.json` (create only if missing and required by caller workflow).
2. Run a lightweight stale-work queue scan:
   - recent low-confidence pages
   - unresolved `^[ambiguous]` markers
   - pending supersession review items
3. Return a compact preflight summary for the caller skill.

## Optional Actions

- If `status_snapshot=true`, append a single `SESSION_START` line to `log.md` with the current timestamp and goal.
- If caller requests audit visibility, append one `_meta/audit.jsonl` entry:
  `{"op":"update","skill":"on_session_start","action":"create","page":null,...}`

## Idempotency Guidance

- If called repeatedly in the same workflow window, do not duplicate snapshot writes.
- Derive a deterministic idempotency key from `(date-hour, session_goal, caller)` and skip duplicate log/audit appends for that key.
- Re-running read-only checks is always allowed.

## Safety Rules

- Never delete/archive/rebuild from this hook.
- If any optional action fails, **degrade gracefully**: return warnings and continue the primary workflow.
- This hook may recommend follow-up actions, but must not silently execute destructive changes.

## Audit Expectations

- Read-only invocations: no audit entry required.
- Any write-path side effect (log snapshot, generated checklist page): append exactly one line to `_meta/audit.jsonl` after successful write.

## worked example

Trigger payload:

```json
{
  "event": "session_start",
  "vault_path": "/vault",
  "session_goal": "sync kwiki project learnings",
  "collaboration_mode": "multi-agent",
  "status_snapshot": true
}
```

Ordered action sequence:
1. Validate `/vault/index.md`, `/vault/log.md`, `/vault/.manifest.json`
2. Scan recent stale/ambiguous queue
3. Append one line to `/vault/log.md`:
   `- [2026-04-15T11:00:00Z] SESSION_START goal="sync kwiki project learnings" mode=multi-agent`
4. Append one audit line to `/vault/_meta/audit.jsonl`
5. Return preflight summary to caller

Expected bookkeeping updates:
- `index.md`: unchanged
- `log.md`: +1 `SESSION_START` line
- `.manifest.json`: unchanged
- `_meta/audit.jsonl`: +1 append-only entry
