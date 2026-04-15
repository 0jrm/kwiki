---
name: entity-extract
description: >
  Extract typed entities and relationships from wiki page content. Invoked by wiki-ingest after
  each page write. Appends to _graph/entities.jsonl and _graph/edges.jsonl with dedupe by
  (type, normalized_name). Use this skill when the user wants to build or update the typed
  knowledge graph, or when wiki-ingest calls it post-write to record entity provenance.
---

# Entity Extract — Typed Knowledge Graph Builder

You are extracting typed entities and relationships from a wiki page and recording them in the vault's graph layer (`_graph/entities.jsonl`, `_graph/edges.jsonl`). This is called by `wiki-ingest` after each page write — the output populates the page's `entities:` frontmatter and gives later skills (graph traversal, hybrid search, contradiction detection) a structured graph to walk.

## Before You Start

1. Read the target wiki page (content + frontmatter, especially `sources`, `confidence`, and existing `entities:` if present).
2. Read `_graph/entities.jsonl` (if it exists) to build an in-memory dedup index.
3. Read `_graph/edges.jsonl` (if it exists) to build an in-memory edge index.
4. If `_graph/` doesn't exist yet, create the directory and touch both files — this is a first-run condition, not an error.

## Entity Types

Fixed vocabulary — map anything unrecognized to the closest type or skip it.

| Type | Definition |
|---|---|
| `person` | A named individual — researcher, engineer, author, team member |
| `project` | A software project, product, codebase, or initiative |
| `library` | A code library, framework, package, or tool (e.g. `rank_bm25`, `react`) |
| `concept` | An abstract idea, algorithm, pattern, or mental model |
| `file` | A named file, directory, config, or data artifact |
| `decision` | A named architectural or design decision (often carries a date or context) |

> **Unrecognized types:** "tool" → `library`, "organization" / "company" → `concept` (or skip if not prominent), "technique" → `concept`. When in doubt, skip — sparse graph > polluted graph.

## Edge Types

Fixed vocabulary — pick the most specific type that applies.

| Type | Semantics |
|---|---|
| `uses` | A project/skill/concept actively uses the target |
| `depends_on` | Hard dependency — target must exist for source to function |
| `contradicts` | Source and target make conflicting claims |
| `caused` | Source is the root cause of target (used for bugs, incidents, decisions) |
| `fixed` | Source resolves or fixes the target |
| `supersedes` | Source replaces the target (newer version, redesign, retraction) |
| `mentions` | Source references the target without a stronger typed relationship |
| `owned_by` | Source is owned/created/maintained by target |
| `related_to` | Semantic affinity with no stronger type available (last resort) |

## JSONL Schema

**`_graph/entities.jsonl`** — one JSON object per line:
```json
{"id": "person:sarah-chen", "type": "person", "name": "Sarah Chen", "attributes": {"role": "engineer"}, "sources": ["journal/2026-04-12.md"], "first_seen": "2026-04-12T10:00:00Z", "last_seen": "2026-04-15T14:22:00Z"}
{"id": "library:rank-bm25", "type": "library", "name": "rank_bm25", "attributes": {"lang": "python"}, "sources": ["concepts/bm25.md"], "first_seen": "2026-04-10T09:00:00Z", "last_seen": "2026-04-10T09:00:00Z"}
```

**`_graph/edges.jsonl`** — one JSON object per line:
```json
{"src_id": "project:kwiki", "dst_id": "library:rank-bm25", "type": "uses", "confidence": 0.8, "sources": ["projects/kwiki.md"], "first_seen": "2026-04-10T09:00:00Z", "last_seen": "2026-04-10T09:00:00Z"}
```

**Required fields (entities):** `id`, `type`, `name`, `attributes` (may be `{}`), `sources`, `first_seen`, `last_seen`.  
**Required fields (edges):** `src_id`, `dst_id`, `type`, `confidence`, `sources`, `first_seen`, `last_seen`.

## Deduplication Rule

Entities are deduped by `(type, normalized_name)`.

**Normalization steps:**
1. Lowercase
2. Strip punctuation (keep hyphens between words)
3. Collapse whitespace
4. Replace spaces with dashes

**ID format:** `{type}:{normalized_name}` — e.g. `person:sarah-chen`, `library:rank-bm25`, `concept:bm25-ranking`.

**On duplicate detection:** union `sources` (deduplicated list), update `last_seen` to the current timestamp, keep `first_seen` from the existing entry. Never create two rows with the same `id`.

**Edge dedup:** An edge is identified by `(src_id, dst_id, type)`. On duplicate: union `sources`, update `last_seen`, recompute `confidence` by source count.

## Edge Confidence

Confidence follows the same ladder as PR #1 `confidence` frontmatter — more independent sources = higher confidence.

| Sources | Confidence |
|---|---|
| 1 | 0.6 |
| 2 | 0.8 |
| 3+ | 0.9 |
| — | Capped at 1.0 |

## The Extraction Process

### Step 1: Read the Page

Read the full page content plus its frontmatter. Note:
- `sources` — which source files contributed (for provenance on edges)
- `confidence` — the page's own confidence, useful as a prior on extracted edges
- Existing `entities:` list (if present) — these are IDs already recorded from a prior run

### Step 2: Identify Entities

Scan the page body for:
- **Proper nouns** — names of people, projects, libraries, tools
- **File paths and config names** → `file` type
- **Named decisions** (look for "we decided", "chosen over", "ADR", date-prefixed decision names) → `decision` type
- **Algorithms, patterns, mental models** → `concept` type

For each candidate: assign a type, derive the normalized name, form the ID.

### Step 3: Identify Relationships

Scan for verb phrases that map to edge types:
- "X uses Y" / "X is built on Y" → `uses`
- "X depends on Y" → `depends_on`
- "X contradicts Y" / "X conflicts with Y" → `contradicts`
- "X caused Y" / "Y was caused by X" → `caused`
- "X fixed Y" / "X resolved Y" → `fixed`
- "X supersedes Y" / "X replaces Y" → `supersedes`
- "X mentions Y" / "X refers to Y" (no stronger verb) → `mentions`
- "X is owned by Y" / "Y created X" → `owned_by`
- Topical overlap with no clear verb → `related_to`

The source entity (subject of the relationship) is typically the page's primary entity or one named in the sentence. The destination is the other named entity.

### Step 4: Load Existing Graph

Read `_graph/entities.jsonl` line by line. Build a map: `{id → entity_object}`.  
Read `_graph/edges.jsonl` line by line. Build a set of known `(src_id, dst_id, type)` tuples.

If either file is missing (first run), create `_graph/` and touch the file.

### Step 5: Merge Entities

For each entity found in Step 2:

1. Normalize the name → compute ID
2. If ID not in existing map: append as a new line to `entities.jsonl`
3. If ID exists: merge — union `sources`, update `last_seen`, rewrite the line

Since `_graph/` files are machine-owned (not hand-edited), a full rewrite of the file is acceptable when merges are needed. For large vaults, prefer a rewrite-on-change approach: write all lines fresh rather than patching individual lines.

### Step 6: Append / Merge Edges

For each edge identified in Step 3:

1. Compute `(src_id, dst_id, type)` key
2. If key is new: append as a new line to `edges.jsonl` with confidence from the ladder
3. If key exists: union `sources`, update `last_seen`, recompute confidence by source count

### Step 7: Write Back

Write the updated `entities.jsonl` and `edges.jsonl` to `_graph/`. Then append an audit entry to `_meta/audit.jsonl`:

```json
{"ts":"<ISO8601-with-ms>","op":"graph-write","skill":"entity-extract","page":"<vault-relative-path>","source":null,"action":"update","session":null}
```

Create `_meta/` if it doesn't exist.

### Step 8: Return Entity IDs

Return the list of entity IDs found on this page to the caller (wiki-ingest). The caller uses this list to populate the page's `entities:` frontmatter field (replace the old list, don't append).

## Worked Example

**Input paragraph:**
> "Sarah Chen fixed the BM25 ranking bug in kwiki by switching from rank_bm25 to a custom implementation. This supersedes the 2026-03 design decision."

**Entities extracted:**

| Name | Type | ID |
|---|---|---|
| Sarah Chen | `person` | `person:sarah-chen` |
| kwiki | `project` | `project:kwiki` |
| rank_bm25 | `library` | `library:rank-bm25` |
| BM25 ranking | `concept` | `concept:bm25-ranking` |
| 2026-03 design decision | `decision` | `decision:2026-03-design-decision` |

**Edges extracted (assuming single source → confidence 0.6):**

```json
{"src_id": "person:sarah-chen", "dst_id": "concept:bm25-ranking", "type": "fixed", "confidence": 0.6, ...}
{"src_id": "project:kwiki", "dst_id": "library:rank-bm25", "type": "uses", "confidence": 0.6, ...}
{"src_id": "concept:bm25-ranking", "dst_id": "decision:2026-03-design-decision", "type": "supersedes", "confidence": 0.6, ...}
```

**`entities:` frontmatter returned to wiki-ingest:**
```yaml
entities: [person:sarah-chen, project:kwiki, library:rank-bm25, concept:bm25-ranking, decision:2026-03-design-decision]
```

## Quality Checklist

After running entity-extract, verify:

- [ ] `_graph/` directory exists (created if missing)
- [ ] Every entity has: `id`, `type`, `name`, `attributes`, `sources`, `first_seen`, `last_seen`
- [ ] Every edge has: `src_id`, `dst_id`, `type`, `confidence`, `sources`, `first_seen`, `last_seen`
- [ ] No duplicate IDs in `entities.jsonl` (dedup ran correctly)
- [ ] No duplicate `(src_id, dst_id, type)` tuples in `edges.jsonl`
- [ ] Edge confidence follows the 0.6 / 0.8 / 0.9 ladder
- [ ] Audit entry appended to `_meta/audit.jsonl` with `op: "graph-write"`
- [ ] Entity IDs returned to caller for `entities:` frontmatter population
