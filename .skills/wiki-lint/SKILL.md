---
name: wiki-lint
description: >
  Audit and maintain the health of the Obsidian wiki. Use this skill when the user wants to check their
  wiki for issues, find orphaned pages, detect contradictions, identify stale content, fix broken wikilinks,
  or perform general maintenance on their knowledge base. Also triggers on "clean up the wiki",
  "what needs fixing", "audit my notes", or "wiki health check".
---

# Wiki Lint — Health Audit

You are performing a health check on an Obsidian wiki. Your goal is to find and fix structural issues that degrade the wiki's value over time.

**Before scanning anything:** follow the Retrieval Primitives table in `llm-wiki/SKILL.md`. Prefer frontmatter-scoped greps and section-anchored reads over full-page reads. On a large vault, blindly reading every page to lint it is exactly what this framework is built to avoid.

## Before You Start

1. Read `.env` to get `OBSIDIAN_VAULT_PATH`
2. Read `index.md` for the full page inventory
3. Read `log.md` for recent activity context

## Operating Modes

By default `wiki-lint` is **self-healing**: it auto-fixes orphans and broken wikilinks. Use `--report-only` to get the old behavior (list issues, make no changes).

- **Default (self-healing):** run all checks, auto-fix orphans + broken wikilinks, report on what was fixed and what couldn't be.
- **`--report-only`:** run all checks, list issues, change nothing. Useful for CI and pre-merge audits.

Checks that cannot be safely auto-fixed (missing frontmatter, stale content, contradictions, provenance drift) are **always reported, never auto-fixed**.

## Lint Checks

Run these checks in order. Report findings as you go.

### 1. Orphaned Pages

An orphan is a page with no incoming `[[wikilinks]]` from any other page.

**How to check:**
- Glob all `.md` files in the vault
- For each page, Grep the rest of the vault for `[[page-name]]` references
- Pages with zero incoming links (except `index.md` and `log.md`) are orphans

**Self-healing (default):**
1. Invoke `cross-linker --use-graph` restricted to this orphan as the target.
2. cross-linker scans all pages for natural mentions of the orphan's title or aliases, and adds links where matches exist.
3. If no natural match is found, skip the page and keep it listed as orphan in the report — a forced link is worse than an orphan.

**Report-only mode:** list the orphan; take no action.

### 2. Broken Wikilinks

A broken wikilink points to a page that doesn't exist.

**How to check:**
- Grep for `\[\[.*?\]\]` across all pages
- Extract the link targets
- Check if a corresponding `.md` file exists

**Self-healing (default):** try three strategies in order.

1. **Fuzzy match within category** — if the link reads `[[BM25 Scoring]]` inside a `concepts/` page, look for the closest title match in `concepts/*.md` (matching bag-of-words or near-exact name). Rewrite the link to the matched page.
2. **Graph alias match** — check `_graph/entities.jsonl` for an entity whose `name` or aliases match the broken link text. If found, rewrite the link to the entity's primary page (same resolution as cross-linker Step 2.5).
3. **Strip to plain text** — if both fail, rewrite `[[broken-link]]` to `broken-link` (plain text) and log the rewrite. A dead `[[link]]` is noise; plain text is honest.

**Report-only mode:** list the broken link and which of the three strategies would apply; change nothing.

### 2a. Quality Score Recomputation

Recompute the `quality:` score for every page using the same heuristic defined in `wiki-ingest/SKILL.md` Step 5a. If a page lacks `quality:`, compute it now (the score will be written on next touch). If the computed score differs from the stored score by > 0.1, update the stored value.

Pages scoring < 0.4 are flagged "low quality" in the report — no auto-fix (quality is a signal, not a blocker). The user decides whether to invest in improving the page.

**Report-only mode:** compute scores, report low-quality pages, don't write scores back.

### 3. Missing Frontmatter

Every page should have: title, category, tags, sources, created, updated.

**Always reported, never auto-fixed** — schema completions are too lossy to generate automatically.

**How to check:**
- Grep frontmatter blocks (scope to `^---` at file heads) instead of reading every page in full
- Flag pages missing required fields

### 3a. Missing Summary (soft warning)

Every page *should* have a `summary:` frontmatter field — 1–2 sentences, ≤200 chars. This is what cheap retrieval (e.g. `wiki-query`'s index-only mode) reads to avoid opening page bodies.

**How to check:**
- Grep frontmatter for `^summary:` across the vault
- Flag pages without it, **but as a soft warning, not an error** — older pages predating this field are fine; the check exists to nudge ingest skills into filling it on new writes.
- Also flag pages whose summary exceeds 200 chars.

**How to fix:**
- Re-ingest the page, or manually write a short summary (1–2 sentences of the page's content).

### 4. Stale Content

Pages whose `updated` timestamp is old relative to their sources.

**How to check:**
- Compare page `updated` timestamps to source file modification times
- Flag pages where sources have been modified after the page was last updated

### 4a. Retention Decay (read-time only)

Compute decayed confidence on every lint run using:

`decayed = base_confidence * exp(-k * days_since_last_confirmed)`

Rate constants:
- `slow`: `k = 0.0015`
- `medium`: `k = 0.005`
- `fast`: `k = 0.02`

Compatibility mapping at read time:
- `low -> slow`
- `high -> fast`

Do not rewrite pages solely to normalize enum names. Keep base `confidence` untouched.

**How to check:**
- For each page, read `confidence`, `last_confirmed`, and `decay_rate` (default confidence=0.5, decay_rate=medium when missing).
- Compute decayed confidence with non-negative day deltas and clamped confidence in [0,1].
- Add a report section `Decayed below threshold` for pages where `decayed < 0.25`.

### 4b. Reconfirm mode (`--reconfirm`)

When `--reconfirm` is provided, process pages in `Decayed below threshold` with explicit branch outcomes:

1. Prompt for each page:
   - **Re-ingest fresh source** (preferred) -> route through ingest flow; ingest updates `last_confirmed`.
   - **Archive page** -> move/mark per existing archive convention.
2. Record outcome in report.

`--reconfirm` supports decisions; it does not mutate base `confidence`.

### 5. Contradictions

Claims that conflict across pages.

**How to check:**
- This requires reading related pages and comparing claims
- Focus on pages that share tags or are heavily cross-referenced
- Look for phrases like "however", "in contrast", "despite" that may signal existing acknowledged contradictions vs. unacknowledged ones

**How to fix:**
- Add an "Open Questions" section noting the contradiction
- Reference both sources and their claims

### 5a. Supersession Hotspots and Ambiguity Backlog

Supersession is lifecycle metadata, not an error. Lint should surface volatility, not auto-fix it.

**How to check:**
- Flag pages with `supersession_count > 3` and at least one supersession in the last 30 days as volatile.
- Count `^[ambiguous]` markers per page; if count > 5, flag for manual reconciliation.
- Never auto-edit supersession history in lint.

### 8a. Tier Health and Promotion Readiness

Lifecycle tiers:
- `working`
- `episodic`
- `semantic`
- `procedural`

**Tier Drift:**
- Flag `semantic`/`procedural` pages for demotion-review when base confidence is low or decayed confidence is high-risk.

**Promotion Opportunities:**
- Flag `working`/`episodic` pages for promotion when evidence thresholds are met:
  - `working -> episodic`: session close or explicit crystallization
  - `episodic -> semantic`: >= 3 reinforcing episodes
  - `semantic -> procedural`: >= 3 semantic facts supporting reproducible steps

**Provenance Gaps:**
- Flag promoted pages missing backlinks/wikilinks to lower-tier source pages listed in `promoted_from`.

No auto-promotion by default; report opportunities and optionally emit actionable command suggestions.

### 6. Index Consistency

Verify `index.md` matches the actual page inventory.

**How to check:**
- Compare pages listed in `index.md` to actual files on disk
- Check that summaries in `index.md` still match page content

### 7. Provenance Drift

Check whether pages are being honest about how much of their content is inferred vs extracted. See the Provenance Markers section in `llm-wiki` for the convention.

**How to check:**
- For each page with a `provenance:` block or any `^[inferred]`/`^[ambiguous]` markers, count sentences/bullets and how many end with each marker
- Compute rough fractions (`extracted`, `inferred`, `ambiguous`)
- Apply these thresholds:
  - **AMBIGUOUS > 15%**: flag as "speculation-heavy" — even 1-in-7 claims being genuinely uncertain is a signal the page needs tighter sourcing or should be moved to `synthesis/`
  - **INFERRED > 40% with no `sources:` in frontmatter**: flag as "unsourced synthesis" — the page is making connections but has nothing to cite
  - **Hub pages** (top 10 by incoming wikilink count) with INFERRED > 20%: flag as "high-traffic page with questionable provenance" — errors on hub pages propagate to every page that links to them
  - **Drift**: if the page has a `provenance:` frontmatter block, flag it when any field is more than 0.20 off from the recomputed value
- **Skip** pages with no `provenance:` frontmatter and no markers — treated as fully extracted by convention

**How to fix:**
- For ambiguous-heavy: re-ingest from sources, resolve the uncertain claims, or split speculative content into a `synthesis/` page
- For unsourced synthesis: add `sources:` to frontmatter or clearly label the page as synthesis
- For hub pages with INFERRED > 20%: prioritize for re-ingestion — errors here have the widest blast radius
- For drift: update the `provenance:` frontmatter to match the recomputed values

### 8. Fragmented Tag Clusters

Checks whether pages that share a tag are actually linked to each other. Tags imply a topic cluster; if those pages don't reference each other, the cluster is fragmented — knowledge islands that should be woven together.

**How to check:**
- For each tag that appears on ≥ 5 pages:
  - `n` = count of pages with this tag
  - `actual_links` = count of wikilinks between any two pages in this tag group (check both directions)
  - `cohesion = actual_links / (n × (n−1) / 2)`
- Flag any tag group where cohesion < 0.15 and n ≥ 5

**How to fix:**
- Run the `cross-linker` skill targeted at the fragmented tag — it will surface and insert the missing links
- If a tag group is large (n > 15) and still fragmented, consider splitting it into more specific sub-tags

## Output Format

Report findings as a structured list:

```markdown
## Wiki Health Report

### Orphaned Pages (N found)
- `concepts/foo.md` — no incoming links

### Broken Wikilinks (N found)
- `entities/bar.md:15` — links to [[nonexistent-page]]

### Missing Frontmatter (N found)
- `skills/baz.md` — missing: tags, sources

### Stale Content (N found)
- `references/paper-x.md` — source modified 2024-03-10, page last updated 2024-01-05

### Decayed below threshold (N found)
- `concepts/foo.md` — base=0.62, decayed=0.21, last_confirmed=2025-11-01, decay_rate=fast

### Contradictions (N found)
- `concepts/scaling.md` claims "X" but `synthesis/efficiency.md` claims "not X"

### Supersession Hotspots (N found)
- `entities/vendor-a.md` — supersession_count=5, last_superseded=2026-04-02 (volatile)
- `concepts/pricing-model.md` — ambiguous markers=7 (manual reconciliation needed)

### Index Issues (N found)
- `concepts/new-page.md` exists on disk but not in index.md

### Missing Summary (N found — soft)
- `concepts/foo.md` — no `summary:` field
- `entities/bar.md` — summary exceeds 200 chars

### Provenance Issues (N found)
- `concepts/scaling.md` — AMBIGUOUS > 15%: 22% of claims are ambiguous (re-source or move to synthesis/)
- `entities/some-tool.md` — drift: frontmatter says inferred=0.10, recomputed=0.45
- `concepts/transformers.md` — hub page (31 incoming links) with INFERRED=28%: errors here propagate widely
- `synthesis/speculation.md` — unsourced synthesis: no `sources:` field, 55% inferred

### Fragmented Tag Clusters (N found)
- **#systems** — 7 pages, cohesion=0.06 ⚠️ — run cross-linker on this tag
- **#databases** — 5 pages, cohesion=0.10 ⚠️

### Tier Drift (N found)
- `skills/deploy-runbook.md` — tier=procedural, decayed=0.18 (demotion review)

### Promotion Opportunities (N found)
- `journal/2026-04-15.md` — tier=working, evidence_count=3 -> eligible for episodic promotion

### Provenance Gaps (N found)
- `concepts/cache-invalidation.md` — tier=semantic, missing backlinks to `promoted_from` pages

### Fixed Automatically (N)
- `path/to/page.md` — broken link `[[X]]` rewritten to `[[Y]]` (fuzzy match, distance 2)
- `path/to/other.md` — broken link `[[Z]]` stripped to plain text (no resolution strategy matched)
- `path/to/orphan.md` — added incoming link from `concepts/foo.md`
```

Each auto-fix is described with enough detail for a human to audit.

**`_meta/audit.jsonl`** — Only append when a page is **actually modified** (not on report-only runs). For each page auto-fixed:
```json
{"ts":"<ISO8601-with-ms>","op":"lint-fix","skill":"wiki-lint","page":"<vault-relative-path>","source":null,"action":"fix","session":null}
```
One entry per page that was modified. If wiki-lint runs in `--report-only` mode, no audit entries.

## After Linting

Update `log.md` with mode flag:
```
- [TIMESTAMP] LINT mode=self-healing|report-only issues_found=N orphans=X broken_links=Y stale=Z contradictions=W prov_issues=P missing_summary=S fragmented_clusters=F fixed=G
```

## Quality Checklist

After linting, verify:
- [ ] Health report produced with all check categories (orphans, broken links, quality scores, missing frontmatter, stale, contradictions, index, provenance, tag clusters)
- [ ] `log.md` updated with LINT entry (includes mode flag)
- [ ] Self-healing ran by default (orphans + broken links auto-fixed where possible)
- [ ] `--report-only` flag preserves pre-PR-#8 list-only behavior when invoked
- [ ] Quality scores recomputed; pages with drift > 0.1 updated
- [ ] Every auto-fix logged to `_meta/audit.jsonl` (only when files actually modified)
- [ ] Decay computed on read; base confidence left unchanged
- [ ] `Decayed below threshold` report generated (`decayed < 0.25`)
- [ ] `--reconfirm` workflow documented with re-ingest/archive outcomes
- [ ] Supersession hotspots detected and reported
- [ ] Ambiguous-claim accumulation detected and reported
- [ ] Tier Drift reported
- [ ] Promotion Opportunities reported
- [ ] Provenance gaps reported
