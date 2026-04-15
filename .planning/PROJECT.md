# Obsidian Wiki v2

## What This Is

Extensions to the `kwiki` skill-based Obsidian wiki framework (a fork of [@Ar9av/obsidian-wiki](https://github.com/Ar9av/obsidian-wiki)) that add memory lifecycle, a typed knowledge graph, hybrid search, quality controls, privacy filters, and audit logging. For users of the LLM Wiki pattern whose vault has grown past ~100 pages and is starting to rot — so the wiki stays useful as it scales instead of becoming a junk drawer. Implementation layers onto the existing 14 skills rather than replacing them.

## Core Value

The wiki earns trust as it scales — knowledge compounds rather than rots, connections aren't lost, and quality, privacy, and provenance accrue automatically. If everything else fails, this must hold: **ingesting more sources should make the wiki more useful, not noisier.**

## Requirements

### Validated

<!-- Inferred from existing kwiki framework (CLAUDE.md, .skills/, README.md). Not formally codebase-mapped via /gsd:map-codebase, but stable and shipping. -->

- ✓ Skill-based agent framework — 14 skills, symlinked to `.claude/.agents/.cursor/.windsurf`
- ✓ Obsidian vault with categorized pages (`concepts/`, `entities/`, `skills/`, `references/`, `synthesis/`, `journal/`, `projects/`)
- ✓ Required frontmatter + `[[wikilinks]]` as the connective tissue
- ✓ Core operations: `wiki-ingest`, `wiki-query`, `wiki-lint`, `wiki-rebuild`
- ✓ Cross-project skills: `wiki-update`, `wiki-query` work from any directory via `~/.obsidian-wiki/config`
- ✓ Manifest + index + chronological log bookkeeping (`.manifest.json`, `index.md`, `log.md`)
- ✓ Visibility tags (`public`/`internal`/`pii`) for content reach control — merged 2026-04 via PR #14
- ✓ Source-specific ingest: `claude-history-ingest`, `codex-history-ingest`, `data-ingest`
- ✓ Maintenance skills: `cross-linker`, `tag-taxonomy`, `wiki-lint`, `wiki-status`
- ✓ Graph export: `wiki-export` (graphml/neo4j outputs)

### Active

<!-- Full v2 = all 15 PRs, ordered by dependency. MVP-5 subset (★) ships first to validate the foundational layer. Each row becomes its own feature branch off v2-integration. -->

**Lifecycle layer**
- [ ] PR #1 ★ `feat: confidence scoring in frontmatter` — `confidence`, `sources_count`, `last_confirmed`, `decay_rate` fields (deps: none)
- [ ] PR #2 `feat: supersession + version chain` — contradicting claims linked not overwritten (deps: #1)
- [ ] PR #3 `feat: retention decay in wiki-lint` — Ebbinghaus decay, flag below-threshold pages (deps: #1)
- [ ] PR #4 `feat: consolidation tiers` — working/episodic/semantic/procedural promotion (deps: #1, #2)

**Graph layer**
- [ ] PR #5 ★ `feat: typed entity + relationship extraction` — `_graph/entities.jsonl`, `_graph/edges.jsonl`, new `entity-extract` skill (deps: none)
- [ ] PR #6 `feat: graph traversal in wiki-query` — walk typed edges during retrieval (deps: #5)
- [ ] PR #7 `feat: hybrid search with RRF fusion` — BM25 + vector + graph, reciprocal rank fusion (deps: #5, #6)

**Quality + safety layer**
- [ ] PR #8 ★ `feat: quality scoring + self-healing lint` — score new pages, auto-fix orphans and broken links (deps: #1)
- [ ] PR #9 `feat: contradiction detection on write` — check new claims against existing, propose resolution (deps: #1, #2, #5)
- [ ] PR #10 `feat: crystallization skill` — `wiki-crystallize` distills session threads into structured digests (deps: #1, #5)
- [ ] PR #11 ★ `feat: ingest-time PII filter` — strip API keys, tokens, emails before write (deps: none)
- [ ] PR #12 ★ `feat: audit log` — append-only `_meta/audit.jsonl` for every operation (deps: none)

**Automation + collaboration layer**
- [ ] PR #13 `feat: event hooks` — `.skills/_hooks/` with `on_session_start`, `on_session_end`, `on_new_source` (deps: most of above)
- [ ] PR #14 `feat: multi-agent mesh sync` — `wiki-sync` skill, conflict resolution across vault states (deps: #1, #12)
- [ ] PR #15 `docs: v2 schema document + migration guide` — the canonical schema; the gist calls this "the real product" (deps: all)

### Out of Scope

- **Non-markdown output formats** — slide decks (Marp), matplotlib charts, timeline visualizations, CSV/JSON exports, briefs. Gist mentions them under "Output formats beyond markdown" but none of the 15 PRs implement them. Can layer on later; orthogonal to the lifecycle/graph/quality foundation.
- **UI / dashboard / visualization** — everything stays agent-driven markdown + JSONL. No GUI over the vault. Keeps the surface area LLM-native and tool-diffable.
- **Public multi-user hosting** — no hosted service, no auth, no per-tenant vaults. PR #14 covers local multi-agent mesh sync only; hosting is a different product.
- **Vector-search backend selection / bundling** — PR #7 uses QMD if `QMD_WIKI_COLLECTION` is set, falls back to 2-stream fusion otherwise. No new vector DB dependency added to v1. User picks their own.

## Context

**Parent repo:** `/home/jrm22n/projects/kwiki/` — fork of `@Ar9av/obsidian-wiki` on GitHub. Actively maintained upstream (recent merges 2026-04 including visibility tags PR #14).

**Working branch:** `v2-integration` — long-lived integration branch. Feature branches (`feat/NN-short-name`) fork off it, PR into it. One eventual batch PR or one-at-a-time rebase upstream, depending on maintainer preference.

**Design doc:** `v2/llm-wiki.md` — extends Karpathy's original LLM Wiki gist with memory-lifecycle, typed-graph, hybrid-search, quality, automation, privacy, and collaboration patterns learned from running the pattern across thousands of sessions.

**Implementation plan:** `obsidian-wiki-v2-gsd-cookbook.md` (parent repo root) — contains the 15-PR slice, per-PR prompts using the "context → constraint → deliverable → verification + plan-first" template, branching strategy, maintainer coordination template (Phase 5), and the schema-document skeleton (Appendix A).

**Implementation surface:** almost exclusively `.skills/<skill-name>/SKILL.md` edits and helper Python in `_lib/`. `.env.example`, `README.md`, `AGENTS.md`/`CLAUDE.md` get touched when new config knobs or capabilities are added. `bash setup.sh` must run cleanly after every `.skills/` change (symlinks).

**Maintainer signal:** Phase 5 of the plan requires opening one coordination issue at `@Ar9av/obsidian-wiki` before pushing PRs. Not yet opened. Upstream merge is a stretch goal, not a v1 blocker — `v2-integration` on the fork is the ship target.

**Existing vault state:** the user runs their own vault (path in `.env`). Test vault pattern is `~/wiki-test-vault` per the plan doc. Real-vault dogfooding is the final verification loop for each PR.

## Constraints

- **Backward compat with existing vaults** — NON-NEGOTIABLE. Any vault without the new frontmatter fields, `_graph/` directory, or `_meta/audit.jsonl` must still work after upgrading. Pages without new fields get sensible defaults (e.g. `confidence=0.5`, `sources_count=1`, `last_confirmed=<mtime>`, `decay_rate="medium"`). Regression here breaks every existing user of the framework.
- **Plan-first prompting discipline** — NON-NEGOTIABLE. Every implementation prompt includes "Plan first. Specifically address: X" before any code is written. Catches 80% of misunderstandings before they become diffs. This is the working style, not a one-off.
- **Ship target** — all target PRs land on `v2-integration` on the local fork. Upstream merge is a stretch; no upstream approval is required to call v1 done.
- **Structure** — skill instructions in `.skills/<name>/SKILL.md`. Shared helpers in `.skills/<name>/_lib/` with unit tests. `bash setup.sh` must pass after every skill change.
- **Branching** — `main` tracks upstream. `v2-integration` is long-lived. Feature branches `feat/NN-short-name` PR into `v2-integration` (not into `main`, not into upstream). Rebase weekly against `main` to avoid merge hell.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| `.planning/` lives at parent kwiki root, not in `v2/` | Colocate planning with the `.skills/` code it plans for. `v2/` stays the design-doc scratchpad; one repo, one history | — Pending |
| Ship to `v2-integration` first, upstream as stretch goal | Decouples v1 delivery from maintainer response time. Fork stays useful regardless | — Pending |
| Commit to full 15-PR v2 scope, not weekend MVP-5 | Weekend MVP tempting but the 5-PR subset (★) leaves lifecycle, graph, and collaboration stories half-told. Full vision builds cleaner | — Pending |
| Backward compat locked; graceful-degradation aspirational per PR | Backward compat is non-negotiable. Graceful-degradation (zero-config) is preferred but can be waived with justification on a per-PR basis | — Pending |
| Language per-PR (Python default, not locked) | Python is the helper default and matches the existing framework, but each PR can justify another runtime if needed | — Pending |
| Vector backend BYO (QMD or nothing) | Reuse `QMD_WIKI_COLLECTION` if set; no new vector-DB dependency introduced by v1. Two-stream fallback (BM25 + graph) is the guaranteed path | — Pending |
| `★` marks the weekend MVP-5 subset for dependency-ordering and mid-project scope checks | Even though full scope is committed, the MVP-5 subset (#1, #5, #8, #11, #12) is the "if I had to stop now" checkpoint | — Pending |

---
*Last updated: 2026-04-15 after initialization*
