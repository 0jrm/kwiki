---
phase: 02-quality-and-graph-foundation
plan: 01
subsystem: graph-layer
provides: [entity-extract-skill, graph-jsonl-files, entities-frontmatter, graph-aware-cross-linker]
requires:
  - phase: 01-foundation-and-safety
    provides: [confidence-fields]
affects: [02-02, 04-01, 04-02, 05-01]
tech-stack:
  added: [entity-extract skill]
  patterns: [typed-knowledge-graph, append-only-jsonl, entity-dedup-by-type-and-name, edge-confidence-ladder]
key-files:
  created:
    - .skills/entity-extract/SKILL.md
  modified:
    - .skills/wiki-ingest/SKILL.md
    - .skills/cross-linker/SKILL.md
    - .skills/llm-wiki/SKILL.md
    - README.md
key-decisions:
  - "Entity types fixed vocabulary: person, project, library, concept, file, decision"
  - "Edge types fixed vocabulary: uses, depends_on, contradicts, caused, fixed, supersedes, mentions, owned_by, related_to"
  - "Dedup by (type, normalized_name); IDs formatted as {type}:{slug}"
  - "Edge confidence ladder: 0.6 (1 source) → 0.8 (2) → 0.9 (3+), capped at 1.0"
  - "entity-extract is a SKILL.md-only change; no Python runtime yet (matches framework style)"
  - "setup.sh globs .skills/* so new skill is auto-discovered — no setup.sh edits needed"
---

# Phase 2 Plan 01: Typed Knowledge Graph Layer Summary

**New `entity-extract` skill writes typed entities/edges to `_graph/*.jsonl` after every ingest; wiki-ingest invokes it, cross-linker uses it, llm-wiki documents it.**

## Accomplishments
- New `entity-extract` SKILL.md (207 lines) with full schema, dedup rule, edge-confidence ladder, worked example, and quality checklist
- wiki-ingest Step 6b invokes entity-extract and populates page `entities:` frontmatter
- `entities:` field added to wiki-ingest frontmatter template with field documentation
- cross-linker `--use-graph` mode (Step 2.5) prefers entity-backed matches (+0.2 scoring bonus)
- llm-wiki canonical template (`entities: []`) + Graph Layer section documenting `_graph/` structure
- README skills table and Project Structure listing updated
- setup.sh auto-discovers new skill via glob (no edits needed)
- Backward compat preserved — vaults without `_graph/` or pages without `entities:` still work

## Files Created/Modified
- `.skills/entity-extract/SKILL.md` — new, authoritative skill spec
- `.skills/wiki-ingest/SKILL.md` — Step 6b + frontmatter template + field docs + checklist items
- `.skills/cross-linker/SKILL.md` — Before You Start note + Step 2.5 + scoring bonus + checklist item
- `.skills/llm-wiki/SKILL.md` — canonical template `entities: []` + Graph Layer section + Reference entry
- `README.md` — skills table row + Project Structure entry

## Decisions Made
[see key-decisions in frontmatter above]

## Issues Encountered
None — setup.sh uses `.skills/*/` glob so no hardcoded names to update.

## Next Step
Ready for 02-02-PLAN.md (quality scoring + self-healing lint). 02-02 depends on 02-01 because quality scoring uses the entity count as a signal.
