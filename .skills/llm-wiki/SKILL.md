---
name: llm-wiki
description: >
  The foundational knowledge distillation pattern for building and maintaining an AI-powered Obsidian wiki.
  Based on Andrej Karpathy's LLM Wiki architecture. Use this skill whenever the user wants to understand the
  wiki pattern, set up a new knowledge base, or needs guidance on the three-layer architecture (raw sources →
  wiki → schema). Also use when discussing knowledge management strategy, wiki structure decisions, or how
  to organize distilled knowledge. This is the "theory" skill — other skills handle specific operations
  (ingesting, querying, linting).
---

# LLM Wiki — Knowledge Distillation Pattern

You are maintaining a persistent, compounding knowledge base. The wiki is not a chatbot — it is a **compiled artifact** where knowledge is distilled once and kept current, not re-derived on every query.

## Three-Layer Architecture

### Layer 1: Raw Sources (immutable)

The user's original documents — articles, papers, notes, PDFs, conversation logs, bookmarks, **and images** (screenshots, whiteboard photos, diagrams, slide captures). These are never modified by the system. They live wherever the user keeps them (configured via `OBSIDIAN_SOURCES_DIR` in `.env`). Images are first-class sources: the ingest skills read them via the Read tool's vision support and treat their interpreted content as inferred unless it's verbatim transcribed text. Image ingestion requires a vision-capable model — models without vision support should skip image sources and report which files were skipped.

Think of raw sources as the "source code" — authoritative but hard to query directly.

### Layer 2: The Wiki (LLM-maintained)

A collection of interconnected Obsidian-compatible markdown files organized by category. This is the compiled knowledge — synthesized, cross-referenced, and navigable. Each page has:

- YAML frontmatter (title, category, tags, sources, timestamps)
- Obsidian `[[wikilinks]]` connecting related concepts
- Clear provenance — every claim traces back to a source

The wiki lives at the path configured via `OBSIDIAN_VAULT_PATH` in `.env`.

### Layer 3: The Schema (this skill + config)

The rules governing how the wiki is structured — categories, conventions, page templates, and operational workflows. The schema tells the LLM *how* to maintain the wiki.

On top of this, an additive automation/collaboration layer can be enabled:
- Event hooks in `.skills/_hooks/`: `on_session_start`, `on_new_source`, `on_session_end`
- Mesh sync via `wiki-sync` for deterministic multi-agent reconciliation

These are opt-in. If hooks/sync are never invoked, single-agent behavior remains unchanged.

## Wiki Organization

The vault has two levels of structure: **categories** (what kind of knowledge) and **projects** (where the knowledge came from).

### Categories

Organize pages into these default categories (customizable in `.env`):

| Category | Purpose | Example |
|---|---|---|
| `concepts/` | Ideas, theories, mental models | `concepts/transformer-architecture.md` |
| `entities/` | People, orgs, tools, projects | `entities/andrej-karpathy.md` |
| `skills/` | How-to knowledge, procedures | `skills/fine-tuning-llms.md` |
| `references/` | Summaries of specific sources | `references/attention-is-all-you-need.md` |
| `synthesis/` | Cross-cutting analysis across sources | `synthesis/scaling-laws-debate.md` |
| `journal/` | Timestamped observations, session logs | `journal/2024-03-15.md` |

### Projects

Knowledge often belongs to a specific project. The `projects/` directory mirrors this:

```
$OBSIDIAN_VAULT_PATH/
├── projects/
│   ├── my-project/
│   │   ├── my-project.md      ← project overview (named after project)
│   │   ├── concepts/          ← project-scoped category pages
│   │   ├── skills/
│   │   └── ...
│   ├── another-project/
│   │   └── ...
│   └── side-project/
│       └── ...
├── concepts/                   ← global (cross-project) knowledge
├── entities/
├── skills/
└── ...
```

**When knowledge is project-specific** (a debugging technique that only applies to one codebase, a project-specific architecture decision), put it under `projects/<project-name>/<category>/`.

**When knowledge is general** (a concept like "React Server Components", a person like "Andrej Karpathy", a widely applicable skill), put it in the global category directory.

**Cross-referencing:** Project pages should `[[wikilink]]` to global pages and vice versa. A project's overview page should link to the key concept, skill, and entity pages relevant to that project — whether they live under the project or globally.

**Naming rule:** The project overview file must be named `<project-name>.md`, not `_project.md`. Obsidian's graph view uses the filename as the node label — `_project.md` makes every project appear as `_project` in the graph, making it unreadable. So `projects/my-project/my-project.md`, `projects/another-project/another-project.md`, etc.

Each project directory has an overview page structured like this:

```markdown
---
title: My Project
category: project
tags: [ai, web, backend]
source_path: ~/.claude/projects/-Users-name-Documents-projects-my-project
created: 2026-03-01T00:00:00Z
updated: 2026-04-06T00:00:00Z
---

# My Project

One-paragraph summary of what this project is.

## Key Concepts
- [[concepts/some-api]] — used for core functionality
- [[projects/my-project/concepts/main-architecture]] — project-specific architecture

## Related
- [[entities/some-service]] — deployment platform
```

## Special Files

Every wiki has these files at its root:

### `index.md`
A content-oriented catalog organized by category. Each entry has a one-line summary and tags. Rebuild this after every ingest operation. Format:

```markdown
# Wiki Index

## Concepts
- [[transformer-architecture]] — The dominant architecture for sequence modeling ( #ml #architecture)
- [[attention-mechanism]] — Core building block of transformers ( #ml #fundamentals)

## Entities
- [[andrej-karpathy]] — AI researcher, educator, former Tesla AI director ( #person #ml)
```
**Format rule**: Add a space after the opening `(` and tags.
❌ Don't: `description (#tag)` — breaks tag parsing
✅ Do: `description ( #tag)` — proper spacing and tag parsing

### `log.md`
Chronological append-only record tracking every operation. Each entry is parseable:

```markdown
## Log

- [2024-03-15T10:30:00Z] INGEST source="papers/attention.pdf" pages_updated=12 pages_created=3
- [2024-03-15T11:00:00Z] QUERY query="How do transformers handle long sequences?" result_pages=4
- [2024-03-16T09:00:00Z] LINT issues_found=2 orphans=1 contradictions=1
- [2024-03-17T10:00:00Z] ARCHIVE reason="rebuild" pages=87 destination="_archives/..."
- [2024-03-17T10:05:00Z] REBUILD archived_to="_archives/..." previous_pages=87
```

### `.manifest.json`
Tracks every source file that has been ingested — path, timestamps, what wiki pages it produced. This is the backbone of the delta system. See the `wiki-status` skill for the full schema.

The manifest enables:
- **Delta computation** — what's new or modified since last ingest
- **Append mode** — only process the delta, not everything
- **Audit** — which source produced which wiki page
- **Staleness detection** — source changed but wiki page hasn't been updated

### `_meta/audit.jsonl`

Append-only audit log. Every vault write operation appends one JSON line here. Never delete or rewrite existing lines. Created automatically on the first write (`_meta/` directory created if needed).

**Entry schema:**
```json
{
  "ts": "2026-04-15T10:30:00.000Z",
  "op": "ingest",
  "skill": "wiki-ingest",
  "page": "concepts/ml-fundamentals.md",
  "source": "papers/attention-is-all-you-need.pdf",
  "action": "create",
  "session": null
}
```

| Field | Type | Allowed values | Meaning |
|---|---|---|---|
| `ts` | ISO 8601 with ms | — | Wall-clock time of the operation |
| `op` | string enum | `ingest` \| `update` \| `lint-fix` \| `rebuild` \| `link` \| `tag` \| `delete` | Operation category |
| `skill` | string | e.g. `"wiki-ingest"`, `"wiki-update"`, `"data-ingest"`, `"wiki-lint"`, etc. | Skill that wrote the entry |
| `page` | string \| null | vault-relative path | Page modified; `null` for non-page ops |
| `source` | string \| null | path or identifier | External source that triggered the op; `null` for maintenance ops |
| `action` | string enum | `create` \| `update` \| `delete` \| `link` \| `fix` \| `tag` | Specific change type |
| `session` | string \| null | session ID | Reserved for future hook/mesh-sync use; `null` for now |

**Append pattern:** One entry per page per write, appended **after** a successful write (not before). For bulk operations (batch ingest, rebuild), append one entry per page — not one entry for the whole run.

When `wiki-sync` is used, include sync outcome metadata (`merged`, `requires_review`, `aborted`) and conflict counts by class in the appended record.

## Page Template

When creating a new wiki page, use this structure:

```markdown
---
title: Page Title
category: concepts
tags: [ml, architecture]
aliases: [alternate name]
sources: [papers/attention.pdf]
summary: One or two sentences, ≤200 chars, so a reader (or another skill) can preview this page without opening it.
provenance:
  extracted: 0.72
  inferred: 0.25
  ambiguous: 0.03
confidence: 0.5
sources_count: 1
last_confirmed: 2024-03-15T10:30:00Z
decay_rate: "medium"
supersession_count: 0
tier: "working"
promoted_from: []
promotion_evidence_count: 0
entities: []
quality: 0.72
created: 2024-03-15T10:30:00Z
updated: 2024-03-15T10:30:00Z
---

# Page Title

One-paragraph summary of what this page covers.

## Key Ideas

- The source's central claim, paraphrased directly.
- A generalization the source implies but doesn't state outright. ^[inferred]
- A figure two sources disagree on. ^[ambiguous]

Use [[wikilinks]] to connect to related pages.

## Open Questions

Things that are unresolved or need more sources.

## Sources

- [[references/attention-is-all-you-need]] — Original paper
```

## Provenance Markers

Every claim on a wiki page has one of three provenance states. Mark them inline so the reader (and future ingest passes) can tell signal from synthesis.

| State | Marker | Meaning |
|---|---|---|
| **Extracted** | *(no marker — default)* | A paraphrase of something a source actually says. |
| **Inferred** | `^[inferred]` suffix | An LLM-synthesized claim — a connection, generalization, or implication the source doesn't state directly. |
| **Ambiguous** | `^[ambiguous]` suffix | Sources disagree, or the source is unclear. |

Example:

```markdown
- Transformers parallelize across positions, unlike RNNs.
- This is why they scale better on modern hardware. ^[inferred]
- GPT-4 was trained on roughly 13T tokens. ^[ambiguous]
```

### Supersession pattern (contradiction-safe updates)

Contradiction rule: same entity + same attribute, different asserted value.

When contradiction is decisive (`abs(new_confidence - old_confidence) >= 0.2`), move prior claim into `## Superseded` and annotate:

```markdown
## Superseded
- Model context window is 128k tokens.
  - superseded_on: 2026-04-15T10:30:00Z
  - superseded_by_source: releases/provider-x-2026-04.md
  - previous_confidence: 0.64
```

When confidence delta is small (`< 0.2`), keep both claims and mark each `^[ambiguous]` rather than superseding.

Worked example (before/after):

Before:
```markdown
- Provider X context window is 128k tokens.
```

After contradiction with stronger source:
```markdown
- Provider X context window is 256k tokens.

## Superseded
- Provider X context window is 128k tokens.
  - superseded_on: 2026-04-15T10:30:00Z
  - superseded_by_source: docs/provider-x-release-notes.md
  - previous_confidence: 0.62
```

**Why this syntax:**
- `^[...]` is footnote-adjacent in Obsidian — renders cleanly and never collides with `[[wikilinks]]`.
- Inline (suffix) so a single bullet stays a single bullet.
- Default = extracted means existing pages without markers stay valid.

**Confidence and decay fields** — added to every page created or updated by any ingest skill:

| Field | Type | Meaning | Default |
|---|---|---|---|
| `confidence` | float 0.0–1.0 | Reliability estimate. 0.8+ = multiple independent sources agree. 0.5 = single source or inferred. 0.3 = speculative. | `0.5` |
| `sources_count` | int | Distinct sources that contributed to this page. Increment on each update that adds a new source. | `1` |
| `last_confirmed` | ISO 8601 | When was this content last reviewed and still deemed accurate? Set to ingest time on create; update on substantive edits. | ingest timestamp |
| `decay_rate` | `"slow"` \| `"medium"` \| `"fast"` | How quickly content goes stale. Slow = timeless concepts. Medium = tools, APIs, practices. Fast = versions, pricing, current events. (`low`/`high` are read-time aliases.) | `"medium"` |
| `supersession_count` | int | Number of true contradiction supersessions recorded on this page. | `0` |
| `tier` | `"working"` \| `"episodic"` \| `"semantic"` \| `"procedural"` | Lifecycle tier of this page in the consolidation model. | `"working"` |
| `promoted_from` | list[string] | Source pages/claims that promoted into this page. | `[]` |
| `promotion_evidence_count` | int | Number of reinforcing artifacts supporting the current tier placement. | `0` |

Pages without these fields (existing vaults, pre-v2 pages) are **not retroactively rewritten** — they're treated as `confidence: 0.5`, `decay_rate: "medium"` at read time.

Retention decay is derived at lint/query time (`decayed = base_confidence * exp(-k * days_since_last_confirmed)`) and must not overwrite base `confidence`.

### Consolidation tiers

Tier model:
- `working`: raw, session-local, low-confidence observations
- `episodic`: session summaries with bounded context and provenance
- `semantic`: stable cross-session facts abstracted from episodes
- `procedural`: repeatable workflows/checklists distilled from semantic evidence

Promotion thresholds:
- `working -> episodic`: session close or explicit crystallization
- `episodic -> semantic`: >= 3 episodes reinforce same claim/entity cluster
- `semantic -> procedural`: >= 3 semantic facts support reproducible steps

Promotions compile knowledge upward and preserve lower-tier provenance by default. Use `promoted_from` links and wikilinks between source and promoted pages.

Write-time contradiction handling extends this model: new ingest/crystallization passes must run conflict checks against existing claims and either supersede decisively or preserve both claims with `^[ambiguous]`.

**`quality`** (float, 0.0–1.0): Page health score computed from seven signals (confidence, sources_count, summary presence, wikilink count, entities count, body length, freshness of `last_confirmed`). See `wiki-ingest/SKILL.md` Step 5a for the exact heuristic. Pages scoring < 0.4 are flagged "low quality" by `wiki-lint`. Default: computed at write time; pages without it get a fresh score on next lint run. Not retroactively computed on pages not being touched.

### Graph Layer

The vault maintains a typed knowledge graph alongside the markdown pages:

- **`_graph/entities.jsonl`** — one entity per line, typed by `person`, `project`, `library`, `concept`, `file`, or `decision`. Each has an `id` (`{type}:{slug}`), `name`, `sources`, and timestamps.
- **`_graph/edges.jsonl`** — one relationship per line, with `src_id`, `dst_id`, typed edge (e.g. `uses`, `depends_on`, `supersedes`), confidence, sources, and timestamps.
- **`entities:`** frontmatter field — a list of entity IDs present on the page (format `{type}:{slug}`). Populated automatically by the `entity-extract` skill after each page write.

The `entity-extract` skill populates these files; pages without the `entities:` field continue to work (treated as `[]` at read time). Skills that use the graph: `cross-linker` (graph-aware matching), `wiki-query` (graph traversal in PR #6), and contradiction detection (PR #9).

**Entity types (fixed vocabulary):** `person`, `project`, `library`, `concept`, `file`, `decision`.  
**Edge types (fixed vocabulary):** `uses`, `depends_on`, `contradicts`, `caused`, `fixed`, `supersedes`, `mentions`, `owned_by`, `related_to`.  
**Edge confidence ladder:** 0.6 (1 source) → 0.8 (2) → 0.9 (3+).

#### Query-time graph traversal semantics (`wiki-query`)

Graph data is not just ingest metadata; it is a retrieval signal.

- **Seed set:** Start from direct lexical candidates (title/tag/summary/BM25 hits), then resolve their `entities:` IDs.
- **Depth:** default 1 hop; allow 2 hops only on explicit user request (`deep`, `expand graph`).
- **Edge weights:**
  - `depends_on`, `uses`, `fixed`: `1.0`
  - `supersedes`: `0.8` (prefer forward traversal)
  - `related_to`, `mentions`, `owned_by`: `0.7`
  - `contradicts`: `0.6` (include, but caution-label)
- **Hop decay:** multiply score contribution by `0.75` per hop.
- **Guardrails:** visited-set required; graph expansion supplements direct matches and should not displace strong direct evidence by default.

Worked example:
- Query: "How do we handle stale confidence?"
- Direct match: `[[skills/wiki-lint]]` (contains decay policy)
- Graph hop: `wiki-lint` page links entity `concept:retention-decay`, edge `depends_on` to `concept:confidence-scoring`
- Returned connected page: `[[concepts/confidence-scoring]]` labeled `graph-1hop` with `depends_on`

**Frontmatter summary:** Optionally surface the rough mix at the page level so the user can scan for speculation-heavy pages without reading them:

```yaml
provenance:
  extracted: 0.72   # rough fraction of sentences/bullets with no marker
  inferred: 0.25
  ambiguous: 0.03
```

These are best-effort numbers written by the ingest skill at create/update time. `wiki-lint` recomputes them and flags drift. The block is optional — pages without it are treated as fully extracted by convention.

## Retrieval Primitives

Reading the vault is the dominant cost of every read-side skill. Use the cheapest primitive that can answer the question and **escalate only when the cheaper one is insufficient**. Any skill that needs content from the vault should follow this table rather than jumping straight to full-page reads.

| Need | Primitive | Relative cost |
|---|---|---|
| Does a page exist? What's its title/category/tags? | Read `index.md`; `Grep` frontmatter blocks (scope with a pattern that targets `^---` blocks at file heads) | **Cheapest** |
| 1–2 sentence preview of a page | Read the `summary:` field in its frontmatter | **Cheap** |
| A specific claim or section inside a page | `Grep -A <n> -B <n> "<term>" <file>` — returns only the matching lines plus context | **Medium** |
| Whole-page content | `Read <file>` | **Expensive** — last resort |
| Relationships across pages | `Grep "\[\[.*?\]\]"` across the vault, or walk wikilinks from a known page | Case-by-case |

**The rule:** escalate only when the cheaper primitive can't answer the question. If you can answer from `summary:` fields alone, don't read page bodies. If a grepped section with `-A 10 -B 2` gives you the claim, don't read the whole page. A 500-line page opened to read 15 lines is 485 lines of wasted tokens.

**Why this matters:** a 20-page vault lets you get away with full-vault scans. A 200-page vault does not. The primitives above are how the skills framework scales to large vaults without a database.

Skills that consume this table: `wiki-query`, `cross-linker`, `wiki-lint`, `wiki-status` (insights mode). Any new skill that reads the vault should cite this section rather than reinvent the pattern.

## Core Principles

1. **Compile, don't retrieve.** The wiki is pre-compiled knowledge. When you ingest a source, update every relevant page — don't just create a summary of the source.

2. **Compound over time.** Each ingest should make the wiki smarter, not just bigger. Merge new information into existing pages, resolve contradictions, strengthen cross-references.

3. **Provenance matters.** Every claim should trace to a source. When updating a page, note which source prompted the update.

4. **Mark inferences.** Default sentences are extracted. Mark synthesized claims with `^[inferred]` and contested claims with `^[ambiguous]`. A wiki that hides its guessing rots silently; one that marks it stays trustworthy.

5. **Human curates, LLM maintains.** The human decides what sources to add and what questions to ask. The LLM handles the bookkeeping — updating cross-references, maintaining consistency, noting contradictions.

6. **Obsidian is the IDE.** The user browses and explores the wiki in Obsidian. Everything must be valid Obsidian markdown with working wikilinks.

## Environment Variables

The wiki is configured through environment variables (see `.env.example`). The only required variable is the vault path — everything else has sensible defaults.

- `OBSIDIAN_VAULT_PATH` — Where the wiki lives **(required)**
- `OBSIDIAN_SOURCES_DIR` — Where raw source documents are
- `OBSIDIAN_CATEGORIES` — Comma-separated list of categories
- `CLAUDE_HISTORY_PATH` — Where to find Claude conversation data
- `QMD_WIKI_COLLECTION` — Optional vector stream for `wiki-query` hybrid retrieval (unset = no vector stream)

No API keys are needed — the agent running these skills already has LLM access built in.

### Hybrid retrieval in `wiki-query` (BM25 + graph + optional vector)

`wiki-query` fuses available retrieval streams with Reciprocal Rank Fusion (RRF):

`RRF(d) = Σ_i 1 / (k + rank_i(d))`, default `k = 60`.

Stream composition by environment:
- With `QMD_WIKI_COLLECTION` set and backend reachable: BM25 + graph + vector
- Without `QMD_WIKI_COLLECTION`: BM25 + graph
- Without `_graph/` files: BM25 (+ vector if configured)

Any missing stream degrades gracefully; query still answers from remaining streams.

## Modes of Operation

The wiki supports three ingest modes:

| Mode | When to use | What happens |
|---|---|---|
| **Append** | Small delta, incremental updates | Compute delta via manifest, ingest only new/modified sources |
| **Rebuild** | Major drift, fresh start needed | Archive current wiki to `_archives/`, clear, reprocess all sources |
| **Restore** | Need to go back | Bring back a previous archive |

Use `wiki-status` to see the delta and get a recommendation. Use `wiki-rebuild` for archive/rebuild/restore operations.

### Event hooks

Optional lifecycle hooks can run at operational boundaries:
- `on_session_start`: preflight health and stale-work scan
- `on_new_source`: post-ingest normalization after each source unit
- `on_session_end`: wrap-up summary and crystallization suggestion

Hook invocation is fail-soft and additive. Primary write flows succeed even when optional hook actions fail.

### Mesh sync (`wiki-sync`)

In collaborative mode, run `wiki-sync` before/after large writes. Conflict classes are:
- `non_overlapping`
- `same_page_non_overlapping_sections`
- `same_claim_conflict`
- `structural_conflict`

Only safe classes auto-merge; unresolved cases require explicit review. Local content is preserved unless the user explicitly approves overwrite.

## Reference

For details on specific operations, see the companion skills:
- **wiki-status** — Audit what's ingested, compute delta, recommend append vs rebuild
- **wiki-rebuild** — Archive current wiki, rebuild from scratch, or restore from archive
- **wiki-ingest** — Distill source documents into wiki pages
- **wiki-crystallize** — Distill sessions/threads into structured episodic or semantic digest pages
- **entity-extract** — Extract typed entities and relationships; populate `_graph/` files and `entities:` frontmatter
- **claude-history-ingest** — Ingest Claude conversation history
- **codex-history-ingest** — Ingest Codex CLI session history
- **data-ingest** — Ingest any raw text data
- **wiki-query** — Answer questions against the wiki
- **wiki-lint** — Audit and maintain wiki health; self-healing by default (auto-fixes orphans + broken wikilinks); use `--report-only` for CI/audit mode
- **wiki-setup** — Initialize a new vault
- **wiki-sync** — Reconcile multi-agent wiki states with deterministic, class-based conflict handling
- **on_session_start / on_new_source / on_session_end** — Optional event hooks for session and ingest boundary automation
