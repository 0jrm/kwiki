---
name: on_new_source
description: >
  Ingest-boundary post-write hook for normalization and hygiene tasks after a
  source unit has been successfully processed. Additive, opt-in, and fail-soft.
---

# Hook: on_new_source

Use this hook immediately after a source unit is successfully written and core bookkeeping is complete.

## Trigger Contract

- **when**: After `wiki-ingest`/`wiki-update` finishes writing pages for one source unit and updates manifest/index/log.
- **inputs**:
  - `vault_path` (required)
  - `source_path` (required)
  - `pages_created` (list, optional)
  - `pages_updated` (list, optional)
  - `run_link_hygiene` (`true` | `false`, optional; default `true`)
- **expected side effects**:
  - Optional normalization checks
  - Optional graph/link hygiene follow-up calls
  - Append-only audit entry when any hook-managed write occurs

## Default Actions (safe baseline)

1. Verify PII redaction summary exists for this source run (no rewrite required if already present).
2. Confirm entity extraction ran for touched pages; queue remediation if missing `entities:` fields.
3. Optionally trigger link hygiene pass for touched pages only (not whole-vault destructive cleanup).

## Optional Actions

- Run a scoped cross-link pass for `pages_created + pages_updated`.
- Add one concise `HOOK_ON_NEW_SOURCE` entry in `log.md` when caller asks for operational traceability.

## Idempotency Guidance

- Call once per source unit, not per line/chunk/page fragment.
- For batch ingest, dedupe by `(source_path, content_hash)` and avoid duplicate writes.
- Repeated invocations for the same source should return "already processed" and remain no-op unless forced.

## Safety Rules

- Never delete/archive/rebuild from this hook.
- Hook failures must **degrade gracefully** and never invalidate the primary source ingest/update write.
- If optional graph/link step fails, emit review instructions and continue.

## Audit Expectations

- Any write created by this hook must append one line to `_meta/audit.jsonl`.
- Suggested follow-ups without writes do not produce audit entries.

## worked example

Trigger payload:

```json
{
  "event": "new_source",
  "vault_path": "/vault",
  "source_path": "sources/meeting-notes-2026-04-15.md",
  "pages_created": ["journal/2026-04-15-sync.md"],
  "pages_updated": ["concepts/mesh-sync.md"],
  "run_link_hygiene": true
}
```

Ordered action sequence:
1. Confirm primary ingest bookkeeping already succeeded (`index.md`, `log.md`, `.manifest.json`)
2. Verify PII summary and entity extraction coverage for touched pages
3. Run scoped link hygiene for touched pages
4. Append optional `HOOK_ON_NEW_SOURCE` line to `log.md`
5. Append one audit line for hook write side effects

Expected bookkeeping updates:
- `index.md`: unchanged (unless link hygiene inserts new links requiring summary refresh in caller workflow)
- `log.md`: optional +1 hook trace line
- `.manifest.json`: unchanged (already updated by caller before hook)
- `_meta/audit.jsonl`: +1 append-only entry when hook writes
