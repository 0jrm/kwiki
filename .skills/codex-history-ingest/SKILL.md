---
name: codex-history-ingest
description: >
  Ingest Codex CLI conversation history into the Obsidian wiki. Use this skill when the user wants to mine
  their past Codex sessions for knowledge, import their ~/.codex folder, extract insights from previous coding
  sessions, or says things like "process my Codex history", "add my Codex conversations to the wiki", or
  "what have I discussed in Codex before". Also triggers when the user mentions .codex sessions, rollout files,
  session_index.jsonl, or Codex transcript logs.
---

# Codex History Ingest — Conversation Mining

You are extracting knowledge from the user's past Codex sessions and distilling it into the Obsidian wiki. Session logs are rich but noisy: focus on durable knowledge, not operational telemetry.

This skill can be invoked directly or via the `wiki-history-ingest` router (`/wiki-history-ingest codex`).

## Before You Start

1. Read `.env` to get `OBSIDIAN_VAULT_PATH` and `CODEX_HISTORY_PATH` (default to `~/.codex` if unset)
2. Read `.manifest.json` at the vault root to check what has already been ingested
3. Read `index.md` at the vault root to understand what the wiki already contains

## PII Filter

Codex rollout logs can include injected tool payloads, `.env` file contents, and credentials pasted during sessions. Apply this filter to all source text before extracting knowledge.

**Always redact (context-independent):**
- OpenAI/Anthropic keys: `sk-[A-Za-z0-9]{20,}` → `[REDACTED:api-key]`
- GitHub tokens: `ghp_[A-Za-z0-9]{36}` or `ghs_[A-Za-z0-9]{36}` → `[REDACTED:github-token]`
- AWS access keys: `AKIA[A-Z0-9]{16}` → `[REDACTED:aws-key]`
- Slack tokens: `xoxb-[A-Za-z0-9-]+` or `xoxp-[A-Za-z0-9-]+` → `[REDACTED:slack-token]`
- Bearer tokens in headers: `Bearer [A-Za-z0-9._\-]{20,}` → `[REDACTED:bearer-token]`
- Private key blocks: `-----BEGIN ... PRIVATE KEY-----` through `-----END ... PRIVATE KEY-----` → `[REDACTED:private-key]`
- JWT tokens: strings matching `eyJ[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+` → `[REDACTED:jwt-token]`

**Redact in credential context** (inside `.env` files, config blocks, JSON auth responses):
- Email addresses found alongside API credentials or auth config → `[REDACTED:email]`

**Never redact:**
- Email addresses that are the subject of knowledge distillation (e.g. a page about email deliverability can contain example addresses)
- Hashes, IDs, or opaque strings that are not in a credential-looking context
- Content already labeled `[REDACTED:*]` from a prior pass

**On detection:** Replace the matched text inline with `[REDACTED:pattern-name]`. Append a warning to the ingest summary: `"PII filter: redacted N occurrences (pattern-name, ...)"` — but do **not** abort the ingest. Redact and continue.

## Ingest Modes

### Append Mode (default)

Check `.manifest.json` for each source file. Only process:

- Files not in the manifest (new session rollouts, new index files)
- Files whose modification time is newer than `ingested_at` in the manifest

Use this mode for regular syncs.

### Full Mode

Process everything regardless of manifest. Use after `wiki-rebuild` or if the user explicitly asks for a full re-ingest.

## Codex Data Layout

Codex stores local artifacts under `~/.codex/`.

```
~/.codex/
├── sessions/                          # Session rollout logs by date
│   └── YYYY/MM/DD/
│       └── rollout-<timestamp>-<id>.jsonl
├── archived_sessions/                 # Archived rollout logs
├── session_index.jsonl                # Lightweight index of thread id/name/updated_at
├── history.jsonl                      # Local transcript history (if persistence enabled)
├── config.toml                        # User config (contains history settings)
└── state_*.sqlite / logs_*.sqlite     # Runtime DBs (usually skip)
```

### Key data sources ranked by value

1. `session_index.jsonl` — best inventory source for IDs, titles, and freshness
2. `sessions/**/rollout-*.jsonl` — rich structured transcript events
3. `history.jsonl` — useful fallback/timeline aid if enabled

Avoid ingesting SQLite internals unless the user explicitly asks.

## Step 1: Survey and Compute Delta

Scan `CODEX_HISTORY_PATH` and compare against `.manifest.json`:

- `~/.codex/session_index.jsonl`
- `~/.codex/sessions/**/rollout-*.jsonl`
- `~/.codex/archived_sessions/**` (optional; only if user asks for archived history)
- `~/.codex/history.jsonl` (optional fallback)

Classify each file:

- **New** — not in manifest
- **Modified** — in manifest but file is newer than `ingested_at`
- **Unchanged** — already ingested and unchanged

Report a concise delta summary before deep parsing.

## Step 2: Parse Session Index First

`session_index.jsonl` typically has entries like:

```json
{"id":"...","thread_name":"...","updated_at":"..."}
```

Use it to:

- Build a canonical session inventory
- Prioritize recent/high-signal sessions
- Map rollout IDs to human-readable thread names

## Step 3: Parse Rollout JSONL Safely

Each `rollout-*.jsonl` line is an event envelope with:

```json
{
  "timestamp": "...",
  "type": "session_meta|turn_context|event_msg|response_item",
  "payload": { ... }
}
```

### Extraction rules

- Prioritize user intent and assistant-visible outputs
- Favor `response_item` records with user/assistant message content
- Use `event_msg` selectively for meaningful milestones; ignore pure telemetry
- Treat `session_meta` as metadata (cwd, model, ids), not user knowledge

### Skip/noise filters

- Token accounting events
- Tool plumbing with no semantic content
- Raw command output unless it contains reusable decisions/patterns
- Repeated plan snapshots unless they add novel decisions

### Critical privacy filter

Rollout logs can include injected instructions, tool payloads, and sensitive text. Do not ingest verbatim system/developer prompts or secrets.

- Remove API keys, tokens, passwords, credentials
- Redact private identifiers unless relevant and approved
- Summarize instead of quoting raw transcripts

## Step 4: Cluster by Topic

Do not create one wiki page per session.

- Group by stable topics across many sessions
- Split mixed sessions into separate themes
- Merge recurring concepts across dates/projects
- Use `cwd` from metadata to infer project scope

## Step 5: Distill into Wiki Pages

Route extracted knowledge using existing wiki conventions:

- Project-specific architecture/process -> `projects/<name>/...`
- General concepts -> `concepts/`
- Recurring techniques/debug playbooks -> `skills/`
- Tools/services -> `entities/`
- Cross-session patterns -> `synthesis/`

For each impacted project, create/update `projects/<name>/<name>.md` (project name as filename, never `_project.md`).

### Writing rules

- Distill knowledge, not chronology
- Avoid "on date X we discussed..." unless date context is essential
- Add `summary:` frontmatter on each new/updated page (1-2 sentences, <= 200 chars)
- Add provenance markers:
  - `^[extracted]` when directly grounded in explicit session content
  - `^[inferred]` when synthesizing patterns across events/sessions
  - `^[ambiguous]` when sessions conflict
- Add/update `provenance:` frontmatter mix for each changed page

## Step 6: Update Manifest, Log, and Index

### Update `.manifest.json`

For each processed source file:

- `ingested_at`, `size_bytes`, `modified_at`
- `source_type`: `codex_rollout` | `codex_index` | `codex_history`
- `project`: inferred project name (when applicable)
- `pages_created`, `pages_updated`

Add/update a top-level project/session summary block:

```json
{
  "project-name": {
    "source_path": "~/.codex/sessions/...",
    "last_ingested": "TIMESTAMP",
    "sessions_ingested": 12,
    "sessions_total": 40,
    "index_updated_at": "TIMESTAMP"
  }
}
```

### Update special files

Update `index.md` and `log.md`:

```
- [TIMESTAMP] CODEX_HISTORY_INGEST sessions=N pages_updated=X pages_created=Y mode=append|full
```

**`_meta/audit.jsonl`** — After each page write, append one entry (create `_meta/` if needed):
```json
{"ts":"<ISO8601-with-ms>","op":"ingest","skill":"codex-history-ingest","page":"<vault-relative-path>","source":"<rollout-file-or-session-id>","action":"create","session":null}
```
Use `"action": "update"` if the page already existed. One entry per page, appended after the write succeeds.

## Quality Checklist

After ingesting, verify:
- [ ] Every new page has frontmatter with title, category, tags, sources
- [ ] `index.md`, `log.md`, and `.manifest.json` updated
- [ ] Provenance markers applied; `provenance:` block on each page
- [ ] PII filter ran on source content; any redactions noted in summary
- [ ] Audit entries written to `_meta/audit.jsonl` for all pages created/updated

## Privacy and Compliance

- Distill and synthesize; avoid raw transcript dumps
- Default to redaction for anything that looks sensitive (the PII filter catches structured patterns; use judgment for unstructured sensitive content)
- Ask the user before storing personal/sensitive details
- Keep references to other people minimal and purpose-bound

## Reference

See `references/codex-data-format.md` for field-level parsing notes and extraction guidance.
