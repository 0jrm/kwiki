# Roadmap: Obsidian Wiki v2

## Overview

Extensions to the `kwiki` skill-based framework implementing 15 PRs across four layers — lifecycle, graph, quality+safety, and automation. Work lands on the `v2-integration` branch as feature branches (`feat/NN-short-name`). The MVP-5 subset (PRs #1, #5, #8, #11, #12 ★) completes in Phases 1-2 and validates the foundational layer before the deeper graph and lifecycle work begins. PR #15 (schema doc) ships last as the canonical record of everything built.

## Domain Expertise

None

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Foundation & Safety** — PRs #1 ★ #11 ★ #12 ★ — confidence frontmatter, PII filter, audit log (all dep-free; foundation for everything)
- [x] **Phase 2: Quality + Graph Foundation** — PRs #5 ★ #8 ★ — typed entity/relationship extraction + quality scoring + self-healing lint (completes MVP-5)
- [x] **Phase 3: Lifecycle Layer** — PRs #2 #3 #4 — supersession, retention decay, consolidation tiers (all dep on #1)
- [ ] **Phase 4: Graph Traversal + Hybrid Search** — PRs #6 #7 — walk typed edges in wiki-query + BM25/vector/graph fusion with RRF (dep on #5, #6)
- [ ] **Phase 5: Cross-cutting Intelligence** — PRs #9 #10 — contradiction detection on write + crystallization skill (dep on #1, #2, #5)
- [ ] **Phase 6: Automation + Collaboration** — PRs #13 #14 — event hooks + multi-agent mesh sync (dep on most above)
- [ ] **Phase 7: Schema + Migration Docs** — PR #15 — canonical v2 schema document + migration guide for existing users (dep on all)

## Phase Details

### Phase 1: Foundation & Safety
**Goal**: Land the three dep-free PRs that everything else builds on — confidence scoring in frontmatter (#1), ingest-time PII filter (#11), and append-only audit log (#12). After this phase the ★ foundation is half-done, existing vaults still work, and every future PR has a place to write provenance and metadata.
**Depends on**: Nothing (first phase)
**Research**: Unlikely (internal SKILL.md edits; frontmatter schema additions; standard filter/append patterns)
**Plans**: Complete (4 PLAN.md files, 4 SUMMARY.md files — 2026-04-15)

Plans:
- [x] 01-01: PR #1 — Add `confidence`, `sources_count`, `last_confirmed`, `decay_rate` fields to wiki-ingest and wiki-update; backward compat defaults
- [x] 01-02: PR #11 — Ingest-time PII filter (API keys, tokens, emails) in wiki-ingest and data-ingest before any write
- [x] 01-03: PR #12 — Append-only `_meta/audit.jsonl` for every wiki operation; update all write-path skills
- [x] 01-04: PR #12 (part B) — Extend audit coverage to remaining write-path maintenance/history skills

### Phase 2: Quality + Graph Foundation
**Goal**: Complete the MVP-5 subset with typed entity/relationship extraction (#5) and quality scoring + self-healing lint (#8). After this phase the vault has a typed graph (`_graph/entities.jsonl`, `_graph/edges.jsonl`) and pages auto-score themselves — the foundation for contradiction detection, hybrid search, and mesh sync later.
**Depends on**: Phase 1 (PR #8 deps on #1)
**Research**: Unlikely (entity extraction is an established NLP pattern applied to SKILL.md instructions; quality scoring is internal heuristics; the `entity-extract` skill is a new SKILL.md not a new library)
**Plans**: Complete (2 PLAN.md files, 2 SUMMARY.md files — 2026-04-15)

Plans:
- [x] 02-01: PR #5 — New `entity-extract` skill; `_graph/` directory; write `entities.jsonl` + `edges.jsonl` on ingest
- [x] 02-02: PR #8 — Quality scoring on new pages + auto-fix orphans and broken links in wiki-lint (depends on 02-01)

### Phase 3: Lifecycle Layer
**Goal**: Implement the full memory-lifecycle stack — supersession (#2), retention decay (#3), consolidation tiers (#4). Pages now evolve: contradicting claims link forward rather than overwrite, low-confidence pages decay and get flagged, and content promotes through working/episodic/semantic/procedural tiers automatically.
**Depends on**: Phase 1 (all three dep on #1; #4 also deps on #2)
**Research**: Unlikely (Ebbinghaus decay math and supersession chain logic are internal; no external service or new library; patterns follow existing wiki-lint and wiki-ingest conventions)
**Plans**: Complete (3 PLAN.md files, 3 SUMMARY.md files — 2026-04-15)

Plans:
- [x] 03-01: PR #2 — Supersession + version chain; contradicting claims get `supersedes`/`superseded_by` links instead of overwrites
- [x] 03-02: PR #3 — Retention decay in wiki-lint; Ebbinghaus model, flag below-threshold pages
- [x] 03-03: PR #4 — Consolidation tiers; automatic working→episodic→semantic→procedural promotion logic

### Phase 4: Graph Traversal + Hybrid Search
**Goal**: Make retrieval intelligent — wiki-query now walks typed edges (#6) and fuses BM25 + vector + graph results with reciprocal rank fusion (#7). The typed graph built in Phase 2 becomes queryable as a first-class retrieval signal.
**Depends on**: Phase 2 (#6 deps on #5; #7 deps on #5 and #6)
**Research**: Likely (RRF fusion algorithm and BM25 scoring details; QMD integration if `QMD_WIKI_COLLECTION` set; how to fall back gracefully to 2-stream when no vector backend)
**Research topics**: Reciprocal rank fusion implementation details; BM25 scoring for markdown document sets; QMD collection query API; safe fallback path when `QMD_WIKI_COLLECTION` is unset
**Plans**: TBD

Plans:
- [ ] 04-01: PR #6 — Graph traversal in wiki-query; walk `edges.jsonl` to expand query context with related entities
- [ ] 04-02: PR #7 — Hybrid search: BM25 + vector (QMD if set) + graph scores fused with RRF; 2-stream fallback guaranteed

### Phase 5: Cross-cutting Intelligence
**Goal**: Higher-order reasoning over the vault — contradiction detection checks new claims against existing ones (#9) and proposes resolution; crystallization (#10) distills multi-session threads into structured digests.
**Depends on**: Phase 1 + Phase 2 + Phase 3 (#9 deps #1, #2, #5; #10 deps #1, #5)
**Research**: Unlikely (contradiction detection and crystallization are agent reasoning patterns implemented in SKILL.md; no new library or external service needed)
**Plans**: TBD

Plans:
- [ ] 05-01: PR #9 — Contradiction detection on write; check incoming claims against existing pages, flag conflicts, propose resolution strategy
- [ ] 05-02: PR #10 — `wiki-crystallize` skill; distill session threads and raw notes into structured digests with confidence and provenance

### Phase 6: Automation + Collaboration
**Goal**: Autonomous vault maintenance and multi-agent coordination — event hooks (#13) fire on session boundaries and source ingestion; multi-agent mesh sync (#14) resolves conflicts across concurrent vault states.
**Depends on**: Phase 1 through Phase 5 (#13 deps most above; #14 deps #1 + #12)
**Research**: Likely (event hook architecture choices — file watchers vs. explicit hook calls in SKILL.md; conflict resolution strategy for concurrent vault writes in mesh sync)
**Research topics**: Hook invocation patterns in agent frameworks (explicit call vs. trigger); CRDT or merge strategies for concurrent JSONL/markdown writes; coordination protocol for multi-agent vault ownership
**Plans**: TBD

Plans:
- [ ] 06-01: PR #13 — Event hooks in `.skills/_hooks/`; `on_session_start`, `on_session_end`, `on_new_source` lifecycle triggers
- [ ] 06-02: PR #14 — `wiki-sync` skill; conflict resolution across vault states for multi-agent mesh workflows

### Phase 7: Schema + Migration Docs
**Goal**: Ship the canonical v2 schema document and migration guide for existing users — the definitive reference for every frontmatter field, `_graph/` format, `_meta/` structure, and upgrade path from a v1 vault.
**Depends on**: All phases (PR #15 deps all — documents what was built)
**Research**: Unlikely (documentation of existing decisions; no new implementation)
**Plans**: TBD

Plans:
- [ ] 07-01: PR #15 — Canonical v2 schema document (Appendix A skeleton from obsidian-wiki-v2-gsd-cookbook.md) + migration guide; update README, AGENTS.md, CLAUDE.md

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5 → 6 → 7

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation & Safety | 3/3 | **Complete** | 2026-04-15 |
| 2. Quality + Graph Foundation | 2/2 | **Complete** | 2026-04-15 |
| 3. Lifecycle Layer | 3/3 | **Complete** | 2026-04-15 |
| 4. Graph Traversal + Hybrid Search | 0/2 | Not started | - |
| 5. Cross-cutting Intelligence | 0/2 | Not started | - |
| 6. Automation + Collaboration | 0/2 | Not started | - |
| 7. Schema + Migration Docs | 0/1 | Not started | - |
