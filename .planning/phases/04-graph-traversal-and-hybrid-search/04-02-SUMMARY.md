---
phase: 04-graph-traversal-and-hybrid-search
plan: 02
subsystem: hybrid-search-fusion
provides: [bm25-graph-vector-fusion, rrf-ranking, graceful-fallback]
requires: [graph-traversal-query, typed-graph-jsonl]
affects: [05-01, 05-02]
tech-stack:
  added: []
  patterns: [reciprocal-rank-fusion, stream-level-graceful-degradation, retrieval-explainability]
key-files:
  modified:
    - .skills/wiki-query/SKILL.md
    - .skills/llm-wiki/SKILL.md
    - README.md
key-decisions:
  - "RRF is canonicalized with formula and default constant k=60"
  - "Hybrid retrieval is stream-optional: vector depends on QMD_WIKI_COLLECTION and graph depends on _graph/"
  - "Any single stream failure degrades to remaining streams and never aborts query"
  - "Final fused candidate set is capped before synthesis and includes per-stream rank contribution metadata"
  - "wiki-query explain mode surfaces stream participation and fused score attribution for trust/debugging"
---

# Phase 4 Plan 02: Hybrid Search Fusion Summary

Hybrid retrieval is now documented end-to-end: `wiki-query` combines BM25, graph traversal, and optional vector rankings with RRF and deterministic fallback behavior.

## Accomplishments
- Added explicit hybrid stream generation order (BM25, graph, optional vector) and candidate limits
- Added formal RRF fusion formula (`k=60`) and final ranking guidance
- Added fallback matrix for missing vector backend, missing graph files, and single-stream runtime failures
- Added explainability guidance (`--explain`) including per-stream rank contributions and fused scores
- Aligned `llm-wiki` and README with optional `QMD_WIKI_COLLECTION` semantics and non-failing fallback behavior

## Files Created/Modified
- `.skills/wiki-query/SKILL.md` — hybrid stream generation, RRF fusion, fallback matrix, and explain mode output
- `.skills/llm-wiki/SKILL.md` — canonical hybrid retrieval semantics and optional QMD configuration behavior
- `README.md` — user-facing capability notes for graph traversal and RRF-based hybrid ranking

## Issues Encountered
None.

## Next Step
Phase 4 complete; proceed to Phase 5 (`05-01`) contradiction detection on write.
