---
name: wiki-crystallize
description: >
  Distill one or more sessions/threads into structured digest pages that preserve provenance and
  promote durable knowledge up the lifecycle tiers. Use this when the user asks to crystallize a
  session, compile a thread, turn raw notes into a digest, or convert scattered working notes into
  episodic/semantic wiki artifacts.
---

# Wiki Crystallize — Session-to-Knowledge Distillation

Use this skill to convert transient working notes and session artifacts into durable, structured pages.

## Before You Start

1. Read `~/.obsidian-wiki/config` (preferred) or `.env` (fallback) to get `OBSIDIAN_VAULT_PATH`
2. Read `.manifest.json`, `index.md`, and `log.md` at the vault root
3. Identify crystallization inputs:
   - explicit files provided by the user
   - `_raw/` drafts
   - recent journal/session pages
4. Confirm scope:
   - single thread/session
   - multi-session topic synthesis

## Goal

Produce a digest that is:
- compact enough to read quickly
- rich enough to preserve decisions, rationale, and contradictions
- linked into existing wiki structure with `[[wikilinks]]`
- lifecycle-aware (`working -> episodic -> semantic`)

## Crystallization Output Types

Choose one based on evidence density:

1. **Episodic digest** (default)
   - For one bounded session/thread.
   - Output path: `journal/` or `projects/<name>/journal/`.

2. **Semantic digest**
   - For recurring patterns seen across >= 3 episodes.
   - Output path: `synthesis/` or `projects/<name>/synthesis/`.

3. **Procedural extraction**
   - For reproducible workflows with concrete steps and preconditions.
   - Output path: `skills/` or `projects/<name>/skills/`.

## Step-by-Step Process

### Step 1: Gather candidate material

Collect all relevant notes/pages and normalize them into:
- observations (facts/events)
- decisions (chosen option + rationale)
- open questions (unresolved)
- actionables (next steps, constraints)

### Step 2: Contradiction scan

Before writing the digest:
- compare candidate claims against existing pages on same entities/attributes
- mark uncertain disagreements as `^[ambiguous]`
- for clear disagreements, reference existing supersession chains and prefer latest confirmed claim

If contradiction is unresolved, keep both claims in the digest and include a "Reconciliation Needed" item.

### Step 3: Build digest structure

Use this template:

```markdown
---
title: <digest title>
category: journal|synthesis|skills
tags: [crystallization, ...]
sources: [list of source pages/files]
summary: One or two sentences describing what this digest captures.
provenance:
  extracted: 0.00
  inferred: 0.00
  ambiguous: 0.00
confidence: 0.6
sources_count: 1
last_confirmed: <ISO timestamp>
decay_rate: "medium"
supersession_count: 0
tier: "episodic"
promoted_from: []
promotion_evidence_count: 0
entities: []
quality: 0.0
created: <ISO timestamp>
updated: <ISO timestamp>
---

# <digest title>

## Context
- What span this digest covers and why it matters.

## Key Observations
- Extracted facts.
- Inferred synthesis. ^[inferred]

## Decisions
- Decision + rationale + tradeoff.

## Contradictions / Ambiguities
- Conflicting claim pair with resolution status. ^[ambiguous]

## Operational Takeaways
- Reusable guidance and constraints.

## Open Questions
- Items requiring more evidence.

## Sources
- [[path/to/source-page]]
```

### Step 4: Choose promotion target

- Keep digest at `tier: episodic` if this is first-pass consolidation.
- Promote to `tier: semantic` when >= 3 episodes reinforce the same claim cluster.
- Promote to `tier: procedural` only when repeatable steps emerge from stable semantic evidence.

When promoting:
- retain lower-tier pages (no destructive merge)
- set `promoted_from` with source page paths
- increment `promotion_evidence_count`

### Step 5: Integrate and link

- Add 2-5 `[[wikilinks]]` to related concept/entity/skill pages.
- Update or create target pages for durable facts extracted from the digest.
- If this digest changes existing canonical claims, apply supersession rules instead of overwrite.

### Step 6: Finalize bookkeeping

- Update `.manifest.json` with crystallized source references under the source entry used for this run.
- Update `index.md` with the digest page.
- Append to `log.md`:

`- [TIMESTAMP] CRYSTALLIZE sources=N pages_created=X pages_updated=Y tier=episodic|semantic|procedural`

- Append one audit line per page write to `_meta/audit.jsonl`:

```json
{"ts":"<ISO8601-with-ms>","op":"crystallize","skill":"wiki-crystallize","page":"<vault-relative-path>","source":"<session-or-source-id>","action":"create","session":null}
```

Use `"action":"update"` when modifying an existing page.

## Quality Checklist

- [ ] Digest includes observations, decisions, contradictions, and open questions
- [ ] Contradictions are explicit; unresolved ones marked `^[ambiguous]`
- [ ] Frontmatter includes lifecycle, confidence, provenance, and quality fields
- [ ] Digest links to existing pages and is linked from at least one related page
- [ ] `index.md`, `log.md`, and `_meta/audit.jsonl` updated
- [ ] Promotions (if any) preserve lower-tier provenance and set `promoted_from`
