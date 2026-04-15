# Wiki Schema (v2)

Canonical specification for the v2 layer implemented in this repository.

This document is implementation-aligned: it describes shipped behavior from Phases 1-6. Any item not present in current skill instructions is marked as **not yet implemented** or **optional extension**.

## Status and compatibility

- **Implemented:** confidence lifecycle, supersession history, retention decay, consolidation tiers, typed graph extraction, hybrid retrieval with RRF, write-time contradiction preflight, crystallization, PII filtering guidance, append-only audit logging guidance, event hooks, and mesh sync contracts.
- **Backward compat:** v2 is additive. Old pages remain readable and writable when new fields/files are missing.
- **Graceful fallback:** retrieval and collaboration features degrade to baseline behavior when optional infrastructure is absent (for example missing `_graph/` files or unset `QMD_WIKI_COLLECTION`).

## Entity types

Entity IDs use `type:slug` (dedup key: `(type, normalized_name)`).

| type | id format | required attributes | example |
|---|---|---|---|
| person | `person:<slug>` | `name` | `person:sarah-chen` |
| project | `project:<slug>` | `name` | `project:obsidian-wiki-v2` |
| library | `library:<slug>` | `name` | `library:rank-bm25` |
| concept | `concept:<slug>` | `name` | `concept:reciprocal-rank-fusion` |
| file | `file:<slug>` | `name` | `file:wiki-query-skill-md` |
| decision | `decision:<slug>` | `name` | `decision:rrf-k-60` |

Implementation note: entity extraction is currently specified as skill behavior (documentation-driven), not a bundled runtime parser.

## Relationship types

| type | direction | confidence semantics | example |
|---|---|---|---|
| uses | source -> target | edge confidence ladder | `project -> library` |
| depends_on | source -> target | edge confidence ladder | `feature -> library` |
| contradicts | source -> target | edge confidence ladder + caution in query | `claim A -> claim B` |
| caused | source -> target | edge confidence ladder | `incident -> outcome` |
| fixed | source -> target | edge confidence ladder | `change -> bug` |
| supersedes | source -> target | edge confidence ladder + lifecycle link | `new claim -> old claim` |
| mentions | source -> target | edge confidence ladder | `page -> entity` |
| owned_by | source -> target | edge confidence ladder | `project -> person` |
| related_to | source <-> target (stored directed per write) | edge confidence ladder | `concept -> concept` |

Edge confidence ladder (implemented): `0.6` (1 source), `0.8` (2 sources), `0.9` (3+ sources), capped at `1.0`.

## Frontmatter spec

### Required base fields

| field | type | meaning |
|---|---|---|
| title | string | page title |
| category | string | one of wiki category folders |
| tags | list[string] | controlled and freeform tags |
| sources | list[string] | source references |
| created | ISO date/datetime | creation timestamp |
| updated | ISO date/datetime | last update timestamp |

### V2 additive fields (implemented)

| field | type | default / compatibility | meaning |
|---|---|---|---|
| confidence | float (0-1) | `0.5` for ingest pages, `0.8` for wiki-update project pages | base confidence (not decayed) |
| sources_count | int | `1` compatibility default | number of supporting sources |
| last_confirmed | ISO date/datetime | fallback to page mtime when absent | latest reinforcement time |
| decay_rate | enum | `medium` default; compatibility supports `low|medium|high` aliases | forgetting velocity |
| entities | list[string] | `[]` when missing | entity IDs linked from page |
| quality | float (0-1) | computed on write; absent = unknown | seven-signal quality heuristic |
| supersession_count | int | `0` when absent | number of true supersessions |
| tier | enum | `working` default when lifecycle adopted | lifecycle tier |
| promoted_from | string/null | null when absent | source tier for promoted pages |
| promotion_evidence_count | int | `0` when absent | evidence count for promotion |

### Superseded section shape (implemented)

When contradiction is resolved as true conflict, prior claims move to `## Superseded` with:

- `superseded_on`
- `superseded_by_source`
- `previous_confidence`

## Confidence rules

Implemented behavior:

- Confidence is stored as **base confidence** in frontmatter.
- Decay is derived at read/lint time; base confidence is not rewritten by decay.
- Confidence delta under `0.2` in contradiction resolution is treated as ambiguous (retain both claims with `^[ambiguous]`).

Not yet implemented:

- Any global numeric update formula beyond the documented write-path defaults (for example an automatic incremental equation applied to every reinforcement event).

## Decay constants

Decayed confidence formula (implemented):

`decayed = base_confidence * exp(-k * days_since_last_confirmed)`

| decay_rate | k | half-life (approx) | compatibility mapping |
|---|---:|---:|---|
| slow | 0.0015 | ~462 days | `low -> slow` |
| medium | 0.005 | ~139 days | `medium -> medium` |
| fast | 0.02 | ~35 days | `high -> fast` |

Threshold currently used for stale detection in lint: `decayed < 0.25`.

## Quality threshold

Quality model (implemented): seven weighted signals totaling 1.0, computed on write and checked in lint.

- `quality < 0.4`: flagged for rewrite/review (signal only, not hard block)
- `0.4 <= quality < 0.7`: keep + review as needed
- `quality >= 0.7`: generally healthy

Self-healing lint behavior (implemented):

- Default mode auto-fixes orphan and broken-link issues where safe.
- `--report-only` preserves non-mutating audit mode.
- Missing frontmatter remains report-only (not auto-generated blindly).

## Contradiction and supersession semantics

### Write preflight classes (implemented)

- `no_conflict`
- `possible_conflict`
- `conflict`

### Resolution policy (implemented)

- `possible_conflict`: preserve both claims + mark ambiguity.
- `conflict`: no silent overwrite; route through supersession mechanics.
- `no_conflict`: proceed normally.

### Volatility checks (implemented)

Lint reports supersession hotspots and ambiguity backlogs to flag volatile pages.

## Graph storage schema

### `_graph/entities.jsonl`

One JSON object per line:

```json
{"id":"concept:reciprocal-rank-fusion","type":"concept","name":"Reciprocal Rank Fusion","attributes":{},"sources":["/path/source.md"],"first_seen":"2026-04-15T12:00:00Z","last_seen":"2026-04-15T12:00:00Z"}
```

### `_graph/edges.jsonl`

One JSON object per line:

```json
{"src_id":"project:obsidian-wiki-v2","dst_id":"concept:reciprocal-rank-fusion","type":"uses","confidence":0.8,"sources":["/path/source.md"],"first_seen":"2026-04-15T12:00:00Z","last_seen":"2026-04-15T12:00:00Z"}
```

Backward compat: missing `_graph/` is non-fatal; graph stream is skipped.

## Retrieval schema

Implemented retrieval streams in `wiki-query`:

1. BM25 stream (body/text lexical retrieval).
2. Graph stream (entity-seeded bounded traversal over typed edges).
3. Optional vector stream (enabled only when `QMD_WIKI_COLLECTION` is set).

Fusion is Reciprocal Rank Fusion:

- `score(d) = sum(1 / (k + rank_i(d)))`
- canonical constant `k = 60`

Operational constraints (implemented in documentation):

- bounded candidate lists per stream
- fused top set sent to synthesis
- single stream failure degrades to remaining streams, query does not abort
- `--explain` exposes per-stream ranks and fused contributions

No-entity case (implemented behavior): graph stream may be empty; fusion proceeds with non-empty streams.

## PII patterns

Implemented pattern classes in ingest paths:

- API key/token prefixes (`sk-`, `ghp_`, `ghs_`, `AKIA`, `xoxb`, `xoxp`)
- bearer tokens
- private key blocks
- JWT-like tokens (`eyJ...`)
- credential-context email handling (emails are not blanket-redacted when they are the actual knowledge subject)

Mode knobs:

- `WIKI_PII_MODE=redact|hash|leave` (documented as configurable target behavior)
- `WIKI_PII_EMAIL=redact|hash|leave` (documented as configurable target behavior)

Implementation note: current shipped skill guidance emphasizes redact-and-warn behavior and credential-context handling; environment knob enforcement is an **optional extension** if a runtime helper is later added.

## Audit log schema

Audit sink: `_meta/audit.jsonl` (append-only).

Canonical fields:

- `ts`
- `op`
- `actor`
- `target`
- `source`
- `action`
- `session` (currently nullable / reserved)

Operation taxonomy represented across skill workflows includes:

- ingest/edit-like writes
- lint fixes
- rebuild/archive related writes
- query (where documented by skill process)
- crystallize
- sync

Implemented write rule: one entry per page per successful write; append after success.

## Hook event contracts

Implemented hook skills:

- `on_session_start`
- `on_new_source`
- `on_session_end`

Contract semantics:

- explicit and opt-in (no hook call, no behavior change)
- `on_new_source` fires once per source unit after primary bookkeeping
- fail-soft: hook failure cannot invalidate successful primary writes
- hook side effects should remain auditable

## Sync conflict classes

Implemented classes in `wiki-sync`:

- `non_overlapping`
- `same_page_non_overlapping_sections`
- `same_claim_conflict`
- `structural_conflict`

Implemented outcomes:

- `merged`
- `requires_review`
- `aborted`

Policy: auto-merge only safe classes; preserve local writes when unresolved; escalate claim/structural conflicts to review.

## Migration guide

### Preflight

1. Backup vault directory and verify restore path.
2. Work on a branch and run `bash setup.sh` to refresh skill links.
3. Use a smoke vault or subset of pages before full-vault rollout.

### Rollout order (compatibility-first)

1. Foundation and safety (confidence, PII hygiene, audit append behavior).
2. Graph foundation (`entities` field + `_graph/*.jsonl` population).
3. Query upgrades (graph traversal + hybrid retrieval explainability).
4. Automation and collaboration (hooks, then sync workflows).

### Minimum required changes

- None to keep existing vault readable.
- v2 fields are additive; old pages remain readable.
- Missing v2 artifacts (`_graph/`, audit history, tier metadata) should gracefully fallback.

### Optional enhancements

- Enable vector stream by setting `QMD_WIKI_COLLECTION`.
- Adopt lifecycle tiers broadly across existing pages.
- Enforce PII mode knobs via runtime helper if desired.

### Partial adoption behavior

- No `_graph/`: graph retrieval disabled, BM25/query still works.
- No vector backend: BM25 + graph fusion (or BM25-only if graph also absent).
- No hooks: ingest/update flows remain baseline.
- No sync usage: single-agent workflows unchanged.
- Missing lifecycle fields: lint/query apply compatibility defaults and report where appropriate.

### Validation checklist

- `index.md`, `log.md`, and `.manifest.json` remain coherent after ingest.
- Run lint in `--report-only` first, then self-healing mode.
- Run `wiki-query --explain` and verify stream contributions/fallback.
- Confirm `_meta/audit.jsonl` receives append-only entries after write operations.

### Rollback

1. Restore vault backup.
2. Rerun `bash setup.sh` if skills/symlinks drifted.
3. Disable optional knobs (for example unset vector collection env vars) and resume baseline flow.

## Known gaps and future extensions

- **Not yet implemented:** a single executable runtime package that enforces every documented behavior uniformly across all skills.
- **Not yet implemented:** strict machine-validated schemas for JSONL rows and frontmatter.
- **Optional extension:** stronger PII mode enforcement through dedicated `_lib/pii.py` runtime helper.
- **Optional extension:** expanded entity/relationship taxonomy and alias resolution learning.
- **Optional extension:** richer sync conflict tooling (batch review UI, assisted conflict rewrites).
