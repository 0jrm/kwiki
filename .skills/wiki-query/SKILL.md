---
name: wiki-query
description: >
  Answer questions by searching the compiled Obsidian wiki. Use this skill when the user asks a question
  about their knowledge base, wants to find information across their wiki, asks "what do I know about X",
  "find everything related to Y", or wants synthesized answers with citations from their wiki pages.
  Also use when the user wants to explore connections between topics in their wiki. Works from any project.
  Includes an index-only fast mode triggered by "quick answer", "just scan", "don't read the pages",
  "fast lookup" — returns answers from page summaries and frontmatter without reading page bodies.
---

# Wiki Query — Knowledge Retrieval

You are answering questions against a compiled Obsidian wiki, not raw source documents. The wiki contains pre-synthesized, cross-referenced knowledge.

## Before You Start

1. Read `~/.obsidian-wiki/config` to get `OBSIDIAN_VAULT_PATH` (works from any project). Fall back to `.env` if you're inside the obsidian-wiki repo.
2. Read `$OBSIDIAN_VAULT_PATH/index.md` to understand the wiki's scope and structure

## Visibility Filter (optional)

By default, **all pages are returned** regardless of visibility tags. This preserves existing behavior — nothing changes unless the user asks for it.

If the user's query includes phrases like **"public only"**, **"user-facing"**, **"no internal content"**, **"as a user would see it"**, or **"exclude internal"**, activate **filtered mode**:

- Build a **blocked tag set**: `{visibility/internal, visibility/pii}`
- In the Index Pass (Step 2), skip any candidate whose frontmatter tags contain a blocked tag
- In Section/Full Read passes (Steps 3–4), do not read or cite any blocked page
- Synthesize the answer **only from allowed pages** — do not mention that excluded pages exist

Pages with no `visibility/` tag, or tagged `visibility/public`, are always included.

In filtered mode, note the filter in the Step 6 log entry: `mode=filtered`.

## Retrieval Protocol

**Follow the Retrieval Primitives table in `llm-wiki/SKILL.md`.** Reading is the dominant cost of this skill — use the cheapest primitive that answers the question and escalate only when it can't. Never jump straight to full-page reads.

`wiki-query` now uses a **hybrid retrieval stack**:
- BM25 lexical ranking (always on)
- graph traversal ranking from `_graph/entities.jsonl` + `_graph/edges.jsonl` (when present)
- vector ranking via QMD (only when `QMD_WIKI_COLLECTION` is configured and query succeeds)

Fusion uses **Reciprocal Rank Fusion (RRF)** with default `k = 60`:

`RRF(d) = Σ_i 1 / (k + rank_i(d))`

Where each retriever `i` contributes a rank position for candidate `d`.

### Step 1: Understand the Question

Classify the query type:
- **Factual lookup** — "What is X?" → Find the relevant page(s)
- **Relationship query** — "How does X relate to Y?" → Find both pages and their cross-references
- **Synthesis query** — "What's the current thinking on X?" → Find all pages that touch X, synthesize
- **Gap query** — "What don't I know about X?" → Find what's missing, check open questions sections

Also decide the **mode**:
- **Index-only mode** — triggered by "quick answer", "just scan", "don't read the pages", "fast lookup". Stops at Step 3. Answers from frontmatter + `index.md` only.
- **Normal mode** — the full tiered pipeline below.

### Step 2: Index Pass (cheap)

Build a candidate set *without opening any page bodies*:

- You've already read `index.md` above — use it as the first filter. It lists every page with a one-line description and tags.
- Use `Grep` to scan page **frontmatter only** for title, tag, alias, and summary matches. A pattern like `^(title|tags|aliases|summary):` scoped to vault `.md` files is far cheaper than content grep.
- Collect the top 5–10 candidate page paths ranked by:
  1. Exact title or alias match
  2. Tag match
  3. Summary field contains the query term
  4. `index.md` entry contains the query term

If you're in **index-only mode**, stop here. Answer from `summary:` fields, titles, and `index.md` descriptions only. Label the answer clearly: **"(index-only answer — page bodies not read; facts below are from page summaries and may miss nuance)"**. Then skip to Step 5.

### Step 2b: Candidate Stream Generation (hybrid input stage)

Build up to three ranked candidate streams in parallel. Each stream should return **at most 20 candidates**.

#### Stream A: BM25 lexical (required)

- Build a document set from candidate pages discovered in Step 2 (expand with additional title/tag hits as needed).
- Rank with BM25 over body text and high-signal frontmatter (`title`, `summary`, `tags`).
- Keep top 20 as `bm25_ranked`.

#### Stream B: Graph traversal (optional, fallback-safe)

**GUARD:** If `_graph/entities.jsonl` or `_graph/edges.jsonl` is missing, unreadable, or empty, skip this stream with no hard failure.

When graph data exists:
1. Build seed pages from strong Step 2/BM25 matches.
2. Resolve seed pages to entity IDs from page frontmatter `entities:`. If missing, treat as `[]`.
3. Optionally backfill seed entities by matching page titles/aliases against `_graph/entities.jsonl` names.
4. Traverse `_graph/edges.jsonl` with bounded walk:
   - default depth: **1 hop**
   - depth **2 hops** only when user explicitly asks ("deep", "expand graph", "broaden context")
5. Use edge-type weights:
   - `depends_on`, `uses`, `fixed`: `1.0`
   - `supersedes`: `0.8` (prefer forward direction)
   - `related_to`, `mentions`, `owned_by`: `0.7`
   - `contradicts`: `0.6` (include with caution)
6. Apply hop decay multiplier `0.75^hop`.
7. Maintain a visited set to prevent loops and duplicate expansion.
8. Convert expanded entities back to candidate pages via matching `entities:` frontmatter.

Provenance labels for graph-derived candidates:
- `graph-1hop`
- `graph-2hop`

If a candidate path includes a `contradicts` edge anywhere, add a caution label (`graph-contradiction-path`) and lower tie-break priority.

#### Stream C: Vector (optional — requires `QMD_WIKI_COLLECTION` in `.env`)

**GUARD: If `$QMD_WIKI_COLLECTION` is empty or unset, skip this entire step and proceed to Step 3.**

> **No QMD?** Skip to Step 3 and use `Grep` directly on the vault. QMD is faster and concept-aware but the grep path is fully functional. See `.env.example` for setup.

If `QMD_WIKI_COLLECTION` is set and the index pass didn't produce clear candidates — or the question requires semantic matching rather than exact terms — use QMD to build a vector-ranked stream:

```
mcp__qmd__query:
  collection: <QMD_WIKI_COLLECTION>   # e.g. "knowledge-base-wiki"
  intent: <the user's question>
  searches:
    - type: lex    # keyword match — good for exact names, file paths, error messages
      query: <key terms>
    - type: vec    # semantic match — good for concepts, patterns, "what is X like"
      query: <question rephrased as a description>
```

The returned snippets act as pre-read section summaries. Keep top 20 as `vector_ranked`.

**Also search `papers` when the question may have source material in `_raw/`:**

If `QMD_PAPERS_COLLECTION` is set and the user is asking about a topic likely covered by ingested papers (research, theory, background), run a parallel search against the papers collection. Cite raw sources separately from compiled wiki pages in your answer.

### Step 2c: Fusion + fallback logic

Combine available streams with RRF (`k=60`) and produce a final ranked list.

Fallback behavior is mandatory:
- If vector stream is unavailable/fails: fuse BM25 + graph
- If graph stream is unavailable/fails: fuse BM25 + vector (if vector exists)
- If both optional streams unavailable/fail: BM25-only
- Any single stream failure must degrade gracefully and never abort query execution

Fusion output:
- top **10** pages before synthesis
- each result carries:
  - `fused_score`
  - `streams_used` (e.g., `bm25,graph`)
  - per-stream rank contributions (e.g., `bm25:3, graph:7, vector:2`)
  - provenance (`direct-match`, `graph-1hop`, `graph-2hop`)

Safety rule: graph/vector expansion adds context, but strong direct lexical matches should win normal tie-breaks.

### Step 3: Section Pass (medium cost — only if Steps 2/2b/2c are inconclusive)

For each of the top candidates, pull the relevant section *without reading the whole page*:

- Use `Grep -A 10 -B 2 "<query-term>" <candidate-file>` to get just the lines around the match.
- This usually returns 15–30 lines per hit instead of 100–500.
- If the section grep gives a clear answer, go straight to Step 5.

### Step 4: Full Read (expensive — last resort)

Only when Steps 2 and 3 don't answer the question:

- `Read` the top **3** candidates in full.
- Follow at most one hop of `[[wikilinks]]` from those pages if the answer requires cross-references.
- Check "Open Questions" sections for known gaps.
- If you're still short, **then** fall back to a broad content grep across the vault. Tell the user you escalated — this is the expensive path and they should know.

### Step 5: Synthesize an Answer

Compose your answer from wiki content:
- Cite specific wiki pages using `[[page-name]]` notation
- Note which step the answer came from ("found in summary" vs "grepped section" vs "full page read") — helps the user understand confidence
- If the wiki has contradictions, present both sides
- If the wiki doesn't cover something, say so explicitly
- Suggest which sources might fill the gap
- When graph evidence contributed, include provenance labels inline for key claims (for example: "from `graph-1hop` via `depends_on`")

### Step 5b: Optional explain mode (`--explain`)

If the user asks for `--explain`, include retrieval diagnostics:
- stream availability (`bm25`, `graph`, `vector`)
- skipped streams and reason (unset env var, missing `_graph`, backend error)
- per-result rank table (`bm25`, `graph`, `vector`, `fused_score`)
- graph traversal metadata (`depth`, edge types used, contradiction-path flags)

### Step 6: Log the Query

Append to `log.md`:
```
- [TIMESTAMP] QUERY query="the user's question" result_pages=N mode=normal|index_only|filtered escalated=true|false
```

## Answer Format

Structure answers like this:

> **Based on the wiki:**
>
> [Your synthesized answer with [[wikilinks]] to source pages]
>
> **Pages consulted:** [[page-a]], [[page-b]], [[page-c]]
>
> **Gaps:** [What the wiki doesn't cover that might be relevant]

## Retrieval Checklist

- [ ] RRF formula and default `k = 60` are explicit in query flow
- [ ] Query works with and without `_graph/` files
- [ ] 2-stream fallback (BM25 + graph) is explicit when vector is unavailable
- [ ] Any stream failure degrades gracefully; query still returns results
- [ ] Traversal depth, edge weights, and hop decay are explicit
- [ ] Graph-derived snippets/results are provenance-labeled in output
