# GSD Cookbook: Implementing LLM Wiki v2 in `obsidian-wiki`

A step-by-step, prompt-included playbook for forking [Ar9av/obsidian-wiki](https://github.com/Ar9av/obsidian-wiki) and shipping the [LLM Wiki v2](https://gist.github.com/rohitg00/2067ab416f7bbe447c1977edaaa681e2) improvements as a coherent series of pull requests.

GSD philosophy here:
- **Slice by capability, not by file.** Each PR delivers one user-visible improvement end-to-end.
- **Ship the smallest thing that works**, then layer.
- **Schema first, automation last.** Get the data model right before wiring hooks.
- **Use Claude Code as your pair**, but you drive the architecture decisions.

---

## Phase 0 — Pre-flight (15 min)

### What you need installed
- `git` (any modern version)
- `gh` (GitHub CLI) — `brew install gh` on Mac, then `gh auth login`
- `node` 20+ (for `npx skills add` if you want to test the published path)
- `python` 3.10+ (the repo is 60% Python)
- An AI coding agent — the cookbook assumes **Claude Code**, but every prompt works in Cursor or Codex with minor tweaks
- An Obsidian vault directory you don't mind being a guinea pig (create `~/wiki-test-vault` if you don't have one)

### What to read before you start
1. The original [Karpathy LLM Wiki gist](https://gist.github.com/karpathy/) — sets the baseline
2. The [v2 gist](https://gist.github.com/rohitg00/2067ab416f7bbe447c1977edaaa681e2) you pasted — the spec we're implementing
3. The `obsidian-wiki` README and any existing `SKILL.md` files in `.skills/` — so you know the patterns the repo already follows

> **GSD principle:** spend 30 min reading the existing skill files. The repo already has conventions (frontmatter shape, command naming, manifest format). Match them. New code that matches existing patterns gets merged. New code that invents its own world gets bikeshedded.

---

## Phase 1 — Fork, Clone, Branch (10 min)

### Step 1.1 — Fork on GitHub
Go to https://github.com/Ar9av/obsidian-wiki and click **Fork**. Name it `obsidian-wiki` under your account. Don't uncheck "copy the main branch only" — we want a clean starting point.

### Step 1.2 — Clone your fork locally
```bash
cd ~/projects   # or wherever you keep code
gh repo clone YOUR_USERNAME/obsidian-wiki
cd obsidian-wiki

# Add the upstream remote so you can pull future updates
git remote add upstream https://github.com/Ar9av/obsidian-wiki.git
git remote -v   # verify: origin = your fork, upstream = Ar9av's
```

### Step 1.3 — Create the long-lived integration branch
All v2 work lands here first, then individual feature branches PR into it. This keeps your `main` clean and trackable against upstream.

```bash
git checkout -b v2-integration
git push -u origin v2-integration
```

### Step 1.4 — Run the existing setup so you have a working baseline
```bash
cp .env.example .env
# Edit .env: set OBSIDIAN_VAULT_PATH=~/wiki-test-vault
bash setup.sh
```

Confirm the baseline works before you change anything. In a fresh terminal:
```bash
cd ~/projects/obsidian-wiki
claude   # or your agent of choice
```
Then in the agent: `/wiki-setup`, drop a markdown file in `~/wiki-test-vault/_raw/`, run `/wiki-ingest`, and verify a wiki page got created. **Do not skip this.** If the baseline is broken on your machine, you'll waste a day debugging your changes.

---

## Phase 2 — Plan the Slices (30 min)

The v2 gist describes ~10 capability areas. Here's how to slice them into shippable PRs, ordered by dependency and value-per-effort:

| # | PR Title | What it adds | Depends on | Est. size |
|---|---|---|---|---|
| 1 | `feat: confidence scoring in frontmatter` | Adds `confidence`, `sources_count`, `last_confirmed`, `decay_rate` to page frontmatter; updates `wiki-ingest` and `wiki-lint` to write/read it | none | S |
| 2 | `feat: supersession + version chain` | When a new claim contradicts an existing one, link old→new, mark old `superseded_by`, never delete | #1 | S |
| 3 | `feat: retention decay in wiki-lint` | Ebbinghaus-style decay; `wiki-lint` flags pages whose decayed confidence drops below threshold | #1 | M |
| 4 | `feat: consolidation tiers (working/episodic/semantic/procedural)` | Folder convention + promotion skill that lifts observations up the tiers as evidence accumulates | #1, #2 | M |
| 5 | `feat: typed entity + relationship extraction` | New `entity-extract` skill; entities written to `_graph/entities.jsonl`, relationships to `_graph/edges.jsonl` with types | none | M |
| 6 | `feat: graph traversal in wiki-query` | `wiki-query` walks typed edges in addition to grep/QMD | #5 | M |
| 7 | `feat: hybrid search with RRF fusion` | `wiki-query` runs BM25 + vector (QMD) + graph in parallel, fuses with reciprocal rank fusion | #5, #6 | L |
| 8 | `feat: quality scoring + self-healing lint` | Every new page gets a quality score; `wiki-lint` auto-fixes orphans and broken links instead of just listing them | #1 | M |
| 9 | `feat: contradiction detection on write` | `wiki-ingest` checks new claims against existing ones, proposes resolution, requires confirmation only on conflict | #1, #2, #5 | M |
| 10 | `feat: crystallization skill` | New `wiki-crystallize` skill that takes a session/thread and distills it into a structured digest page | #1, #5 | M |
| 11 | `feat: ingest-time PII filter` | Strip API keys, tokens, emails, etc. before anything hits the vault. Configurable via `.env` | none | S |
| 12 | `feat: audit log` | Append-only `_meta/audit.jsonl` for every ingest/edit/delete/query | none | S |
| 13 | `feat: event hooks` | `.skills/_hooks/` directory with `on_session_start`, `on_session_end`, `on_new_source` triggers | most of the above | L |
| 14 | `feat: multi-agent mesh sync` | Conflict-resolution policy + `wiki-sync` skill for merging two vault states | #1, #12 | L |
| 15 | `docs: v2 schema document + migration guide` | The schema document the gist calls "the real product" | all of the above | M |

> **GSD move:** if you only have a weekend, ship PRs **#1, #5, #8, #11, #12**. That's the minimum viable v2 — you get the lifecycle primitive, the graph primitive, real lint, safety, and accountability. Everything else layers on those five.

### Where the work lives in the repo

Almost all of these are new or modified `SKILL.md` files inside `.skills/`. A typical PR touches:
- `.skills/<skill-name>/SKILL.md` — instructions the agent reads
- One or two helper Python scripts under the skill folder if logic is shared
- `.env.example` if you add a new config knob
- `README.md` for the skill table at the bottom
- `CLAUDE.md` / `AGENTS.md` if the bootstrap needs to mention the new capability

Run `bash setup.sh` after every change to a `.skills/` folder so the symlinks pick up new skills.

---

## Phase 3 — Branch + Implement Loop (per PR)

Repeat this loop for each row in the table above. The branching strategy:

```
main (tracks upstream)
└── v2-integration (your long-lived branch)
    ├── feat/01-confidence-scoring
    ├── feat/02-supersession
    ├── feat/03-retention-decay
    └── ...
```

Each feature branch PRs into `v2-integration`. Once `v2-integration` is solid, you open one big PR upstream OR rebase the individual feature branches against `main` and submit them one at a time (the maintainer's preference will dictate — ask in an issue first, see Phase 5).

### The per-PR loop

```bash
# From v2-integration
git checkout v2-integration
git pull origin v2-integration
git checkout -b feat/01-confidence-scoring

# ... do the work with Claude (prompts below) ...

# Verify
bash setup.sh
# In your agent, run the affected skill against the test vault and inspect output

# Commit
git add -A
git commit -m "feat: add confidence scoring to wiki page frontmatter

Adds confidence, sources_count, last_confirmed, and decay_rate fields
to the frontmatter written by wiki-ingest. wiki-lint now reads these
fields and flags pages whose confidence drops below threshold.

Implements the 'memory lifecycle' section of LLM Wiki v2."

git push -u origin feat/01-confidence-scoring

# Open PR into v2-integration (not main)
gh pr create --base v2-integration --title "feat: confidence scoring" --body-file .github/pr-body.md
```

---

## Phase 4 — The Prompts

These are the actual prompts to paste into Claude Code (or your agent), one per PR. Open the agent **inside the `obsidian-wiki` repo directory** so it has the full context.

Each prompt follows the same shape: **context → constraint → deliverable → verification**. That's the GSD prompt template. Memorize it.

---

### Prompt for PR #1 — Confidence Scoring

```
Context: We're implementing LLM Wiki v2 (https://gist.github.com/rohitg00/2067ab416f7bbe447c1977edaaa681e2) 
in this repo, starting with the "memory lifecycle" section. Before you write 
anything, read these files in order:
  1. .skills/wiki-ingest/SKILL.md
  2. .skills/wiki-lint/SKILL.md
  3. .skills/llm-wiki/SKILL.md
  4. README.md (just the "How it works" and "What we added" sections)

Goal: Add confidence scoring to wiki page frontmatter. Every page should track:
  - confidence: float 0.0–1.0
  - sources_count: int (how many distinct sources support this page)
  - last_confirmed: ISO date (last time a source reinforced any claim)
  - decay_rate: "slow" | "medium" | "fast" (architecture = slow, bug = fast)

Constraints:
  - Do NOT change existing frontmatter fields. Only add new ones.
  - Existing pages without these fields should be treated as confidence=0.5, 
    sources_count=1, last_confirmed=<file mtime>, decay_rate="medium".
  - wiki-ingest must write the new fields when creating or updating a page.
    On update, sources_count increments and last_confirmed becomes today.
  - wiki-lint gets a new check that lists pages with confidence below 0.3.
  - All changes go in .skills/wiki-ingest/SKILL.md and .skills/wiki-lint/SKILL.md.
    No new skill folders for this PR.

Deliverables:
  1. Updated SKILL.md files
  2. A short worked example in each SKILL.md showing the new frontmatter shape
  3. A one-paragraph addition to README.md under "What we added on top of 
     Karpathy's pattern" describing confidence scoring

Verification: After your changes, walk me through what would happen if I 
ingest the same source twice. Show the frontmatter before and after the 
second ingest.

Do not write code yet. First show me your plan, including the exact 
frontmatter schema and the decision rules for picking decay_rate.
```

> **Why this shape:** the "do not write code yet, show me your plan" is the single most valuable line in any agent prompt. It catches 80% of misunderstandings before they become diffs.

---

### Prompt for PR #2 — Supersession

```
Context: PR #1 (confidence scoring) is merged into v2-integration. Now we 
implement supersession — when a new claim contradicts an old one, we link 
them rather than overwriting. Read .skills/wiki-ingest/SKILL.md and 
.skills/wiki-lint/SKILL.md as they stand on this branch.

Goal: When wiki-ingest detects that a new source contradicts an existing 
claim on a page:
  - Do NOT delete the old claim.
  - Move the old claim to a "## Superseded" section at the bottom of the page, 
    annotated with: superseded_on (date), superseded_by_source (path), 
    previous_confidence (float).
  - The new claim takes its place in the main body.
  - The page's top-level frontmatter gets a supersession_count: int.

Constraints:
  - Detection of contradiction is hard — for this PR, define "contradiction" 
    as: the new source asserts a fact about the same entity-attribute pair 
    that disagrees with what's already written. Use simple LLM-judged 
    comparison; don't try to build a logic engine.
  - When uncertain (confidence delta < 0.2), append the new claim alongside 
    the old one and tag both with ^[ambiguous] instead of superseding.
  - wiki-lint gets a check that surfaces pages with > 3 supersessions in the 
    last 30 days (signal that the page is volatile).

Deliverable: updated SKILL.md files + worked example showing a page before 
and after a supersession event.

Show me the plan before writing.
```

---

### Prompt for PR #3 — Retention Decay

```
Context: PRs #1 and #2 are in. Now we add the forgetting curve. Read the 
"Forgetting" subsection of the v2 gist for the model.

Goal: wiki-lint computes a decayed confidence for each page using:
  decayed = base_confidence * exp(-k * days_since_last_confirmed)
where k is determined by decay_rate:
  slow:   k = 0.0015  (~half-life 1.3 years)
  medium: k = 0.005   (~half-life 4.5 months)
  fast:   k = 0.02    (~half-life 5 weeks)

Constraints:
  - Decay is computed on read, never written back. The frontmatter stores 
    the BASE confidence; decay is a derived view.
  - wiki-lint output gets a new section: "Decayed below threshold" listing 
    pages whose decayed confidence is < 0.25.
  - Add a /wiki-lint --reconfirm flag that, for each below-threshold page, 
    prompts the user to either re-ingest a fresh source (resets last_confirmed) 
    or archive the page.
  - Pure Python helper for the decay math goes in 
    .skills/wiki-lint/_lib/decay.py with a unit test.

Deliverable: updated SKILL.md, the helper + test, and a short table in 
README.md showing the half-lives.

Plan first.
```

---

### Prompt for PR #5 — Entity & Relationship Extraction

(Skipping #4 here — same pattern; see the table for the spec.)

```
Context: We're adding the knowledge graph layer from v2. Read these first:
  - .skills/wiki-ingest/SKILL.md (post-PR-#3 state)
  - .skills/cross-linker/SKILL.md
  - The "Beyond flat pages: the knowledge graph" section of the v2 gist

Goal: Create a new skill `entity-extract` that runs as part of wiki-ingest. 
It produces two append-only files inside the vault:
  _graph/entities.jsonl  — one entity per line: {id, type, name, attributes, sources, first_seen, last_seen}
  _graph/edges.jsonl     — one edge per line:   {src_id, dst_id, type, confidence, sources, first_seen, last_seen}

Entity types (start small, expand later): person, project, library, concept, 
file, decision.

Relationship types: uses, depends_on, contradicts, caused, fixed, supersedes, 
mentions, owned_by, related_to.

Constraints:
  - Entities are deduped by (type, normalized_name). Use a stable id scheme: 
    e.g., "person:sarah-chen" (slugified).
  - Every entity and edge tracks the sources that produced it. Confidence on 
    edges follows the same rules as PR #1 (more sources = higher).
  - wiki-ingest, after writing a page, calls entity-extract on the page 
    content and updates _graph/. Page frontmatter gets an `entities: [id, id, id]` 
    list.
  - cross-linker gets a new mode: --use-graph that prefers wikilinks to entities 
    over raw string matches.

Deliverable: new .skills/entity-extract/SKILL.md, modifications to 
wiki-ingest and cross-linker SKILL.md files, an entry in the README skill 
table.

Plan first. In your plan, include: the exact JSONL schema, the 
deduplication rule, and a worked example of ingesting one paragraph and 
showing what gets written to entities.jsonl and edges.jsonl.
```

---

### Prompt for PR #7 — Hybrid Search with RRF

```
Context: We have entities + edges (PR #5) and graph traversal in queries 
(PR #6). Now we wire the three retrieval streams together. Read 
.skills/wiki-query/SKILL.md and the README's QMD section.

Goal: wiki-query runs three retrievers in parallel and fuses with 
reciprocal rank fusion (RRF):
  1. BM25 over page bodies (use rank_bm25 — already a Python dep)
  2. Vector search via QMD if QMD_WIKI_COLLECTION is set; skip if not
  3. Graph traversal: starting from entities mentioned in the query, walk 
     outward 2 hops over typed edges, weighted by edge confidence

Fusion: RRF with k=60 (standard). Final ranked list of page paths goes to 
the existing answer-synthesis step.

Constraints:
  - Each retriever returns at most 20 candidates. Final fused list is top 
    10 before synthesis.
  - If QMD is unavailable, fall back to two-stream fusion (BM25 + graph). 
    Behavior must remain functional with zero config.
  - Add /wiki-query --explain that prints the per-retriever ranks and the 
    fused score for each result. This is the debug surface you'll need 
    forever — build it now, not later.
  - All retrieval code lives in .skills/wiki-query/_lib/. Each retriever 
    is its own file. RRF in fusion.py. Unit tests for fusion.py with 
    hand-crafted rank lists.

Deliverable: refactored .skills/wiki-query/SKILL.md, the _lib/ files, 
tests, and a benchmark note in the SKILL.md showing latency on a 100-page 
test vault.

Plan first. Specifically: how do you handle the case where the query has 
no entity matches (graph stream returns empty)?
```

---

### Prompt for PR #11 — PII Filter

```
Context: Privacy/governance section of the v2 gist. This is small but 
high-value — ship it early to build maintainer trust.

Goal: Before any source content is written to a wiki page, run it through 
a PII filter. Detect and redact:
  - API keys (common prefixes: sk-, ghp_, AIza, AKIA, etc.)
  - JWT tokens (eyJ... pattern)
  - Email addresses (configurable: redact / hash / leave)
  - Phone numbers
  - Anything in a line tagged `# private` or inside <private>...</private>

Constraints:
  - Implementation goes in .skills/wiki-ingest/_lib/pii.py with thorough 
    unit tests (this code MUST not regress).
  - wiki-ingest calls pii.scrub(text) before writing.
  - Behavior configurable via .env:
      WIKI_PII_MODE=redact   # redact | hash | leave (default: redact)
      WIKI_PII_EMAIL=hash    # redact | hash | leave (default: hash)
  - Add an audit line for every redaction: which source, what kind, where 
    in the file (line number). Logged to _meta/audit.jsonl (PR #12 will 
    formalize the audit log; for now just append).

Deliverable: pii.py, tests, .env.example update, SKILL.md change, README 
update.

Plan first. List every PII pattern you'll detect with a regex and an 
example. I want to see the regexes before you write the code.
```

---

### Prompt for PR #12 — Audit Log

```
Context: We have ad-hoc logging from earlier PRs. Now formalize it.

Goal: Every wiki operation appends one JSON line to _meta/audit.jsonl:
  {ts, op, actor, target, before_hash, after_hash, source, notes}

Operations to log: ingest, edit, delete, supersede, archive, query, 
crystallize, lint-fix, sync.

Constraints:
  - Append-only. Never rewrite or compact this file in code (you can 
    document a manual rotation procedure).
  - actor is read from .env (WIKI_ACTOR=your-name) or defaults to $USER.
  - before_hash / after_hash are SHA-256 of file content before/after the 
    op. For non-file ops (query), they're null.
  - All existing skills get a one-line audit call at the end of their 
    documented procedure. Centralized helper in .skills/_lib/audit.py 
    (create the _lib/ folder if it doesn't exist).
  - New skill `wiki-audit` that pretty-prints recent entries with filters: 
    --since, --op, --actor, --target.

Deliverable: audit.py + tests, audit calls woven into existing SKILL.md 
files, new wiki-audit skill, README update.

Plan first.
```

---

### Generic prompts for the remaining PRs

For #4, #6, #8, #9, #10, #13, #14, #15, follow the same template. The fill-in-the-blanks version:

```
Context: We're on PR #__ of the v2 implementation in obsidian-wiki. 
Already shipped: __. Read these files first: __.

Goal: __ (one sentence, then 2–4 bullets of detail).

Constraints:
  - __ (data model rule)
  - __ (backward compat rule)
  - __ (config / .env rule)
  - __ (where the code lives — usually .skills/<name>/_lib/)
  - __ (test requirement)
  - __ (graceful-degradation rule if external deps are missing)

Deliverable: __

Plan first. Specifically address: __ (the one design question you're 
unsure about).
```

The "Plan first. Specifically address: X" line is what separates a 30-minute back-and-forth from a 3-hour rewrite cycle. **Always name the design question.**

---

## Phase 5 — Talking to the Maintainer

Before you push 15 PRs at the maintainer, open one issue. Use this template:

```markdown
Title: Proposal: implement LLM Wiki v2 patterns (lifecycle, graph, hybrid search)

Hi @Ar9av — really nice work on this framework. I want to implement the 
v2 improvements from rohitg00's gist 
(https://gist.github.com/rohitg00/2067ab416f7bbe447c1977edaaa681e2) on 
top of the existing skills.

I've sliced the work into ~15 PRs, ordered by dependency. The first five 
(confidence scoring, supersession, entity extraction, quality scoring, 
PII filter) form a minimum-viable v2 layer; the rest layer on those.

Before I start sending PRs, two questions:

1. Do you want one large PR per capability area, or do you prefer many 
   small PRs into a long-lived `v2-integration` branch?
2. Is there an existing direction for any of these that I should align 
   with? Particularly curious about the entity-extraction approach — I 
   was planning to write entities to a `_graph/` directory inside the 
   vault but happy to put it elsewhere.

Full plan with PR list and prompts is in this gist: <link to your own 
gist of this cookbook>

Happy to scope down or split differently if any of this is off-base.
```

This costs you 10 minutes and saves you from doing 40 hours of work the maintainer doesn't want. **Always open the issue.**

---

## Phase 6 — Per-PR Checklist (paste into your `.github/pull_request_template.md`)

```markdown
## What
One-sentence description.

## Why
Link to the v2 gist section this implements. Link to the tracking issue.

## How
- [ ] Touches `.skills/<name>/SKILL.md`
- [ ] Helper code in `_lib/` with tests
- [ ] `.env.example` updated if a new knob was added
- [ ] README skill table updated
- [ ] Bootstrap files (CLAUDE.md / AGENTS.md) updated if relevant
- [ ] `bash setup.sh` runs cleanly
- [ ] Manual smoke test against `~/wiki-test-vault` documented in PR description

## Backward compatibility
- [ ] Existing vaults without the new fields/files still work
- [ ] No required new env vars (or: new vars have sensible defaults)

## Verification
Paste the smoke-test transcript: command run, output observed.
```

---

## Phase 7 — Keeping Up With Upstream

The repo is active (the README mentions changes "2 days ago", "last week"). To avoid merge hell:

```bash
# Once a week, sync upstream into your fork
git checkout main
git fetch upstream
git merge upstream/main
git push origin main

# Then rebase your integration branch
git checkout v2-integration
git rebase main
# resolve conflicts, then:
git push --force-with-lease origin v2-integration
```

Each feature branch should be rebased on `v2-integration` before its PR review.

---

## Phase 8 — When You're Stuck

Common failure modes and the GSD response:

**The agent keeps writing code that doesn't match repo conventions.**
→ Stop. In a fresh session, paste an existing `SKILL.md` and say: "This is the style. Match it exactly. Now do X." Style transfer is a one-shot problem; don't fight it across 5 turns.

**The PR is getting too big.**
→ Split it. PR titled "feat: confidence scoring" became 800 lines? Split into "feat: confidence frontmatter schema" (just the spec + read path) and "feat: confidence write path in wiki-ingest" (the writes). Reviewers say yes to small PRs.

**You can't decide between two designs.**
→ Build the dumber one. Ship it. The smarter one will be obvious in 2 weeks once you have usage data. The v2 gist itself says: "All of this is modular. You don't need everything on day one."

**A PR's smoke test fails on real data but passes on test data.**
→ Your test vault is too clean. Drop in 50 pages from a real Obsidian vault (anonymize first using your PR #11 PII filter — eat your own dog food) and re-run. This is how you find the edges.

**The maintainer is slow to respond.**
→ Keep working in your fork. The whole point of `v2-integration` is that it's useful to YOU even if upstream never merges it. If upstream stalls, you've still built the thing you wanted.

---

## Appendix A — The schema document (your final PR)

PR #15 is the most important one. It's the document the v2 gist calls "the real product." Draft it as you build the other PRs — every time you make a design decision (decay constants, entity types, fusion weights, PII patterns), write it down here. By the time you're at PR #15, this document writes itself.

Template skeleton for `.skills/llm-wiki-v2-schema/SCHEMA.md`:

```markdown
# Wiki Schema (v2)

## Entity types
| type | id format | required attributes | example |
| ... |

## Relationship types
| type | direction | confidence rules | example |
| ... |

## Frontmatter spec
(every field, its type, its meaning, its default)

## Decay constants
(decay_rate → k value table, with rationale)

## Confidence rules
- New page: confidence = 0.5
- Each new corroborating source: confidence += (1 - confidence) * 0.3
- Contradiction: confidence -= 0.2 (floor at 0.1)
- Manual confirmation: confidence = max(confidence, 0.85)

## Promotion rules (consolidation tiers)
- Working → Episodic: at session end
- Episodic → Semantic: when 3+ episodes reference the same entity
- Semantic → Procedural: when a workflow emerges across 3+ semantic facts

## Quality threshold
- Below 0.4: auto-flag for rewrite
- 0.4–0.7: keep, mark for review
- Above 0.7: keep, no action

## PII patterns
(table of patterns, each with regex, example, default action)

## Audit log schema
(JSON shape with field meanings)
```

This is the document a future contributor (or a future you) reads to understand what the system actually does. Write it like you're explaining to someone with no context.

---

## Appendix B — Quick command reference

```bash
# Daily loop
git checkout v2-integration && git pull
git checkout -b feat/NN-short-name
# ... work + prompts ...
bash setup.sh                                    # refresh symlinks
# smoke test in agent
git add -A && git commit -m "feat: ..."
git push -u origin feat/NN-short-name
gh pr create --base v2-integration

# Weekly sync
git checkout main && git fetch upstream && git merge upstream/main && git push
git checkout v2-integration && git rebase main && git push --force-with-lease

# Inspect what changed
git log --oneline upstream/main..v2-integration   # your work, not upstream's
git diff upstream/main..v2-integration -- .skills/  # all skill changes
```

---

## Done means done

You're done with v2 when:
1. The 5 minimum-viable PRs are merged into `v2-integration` and the integration branch passes a fresh end-to-end test against a real vault.
2. The schema document (PR #15) describes what you actually built, not what you intended to build.
3. You've used the v2-enabled wiki for two weeks of your own work without falling back to grep.
4. You've opened the upstream PR (or decided, with reasons, that your fork is the long-term home).

That's it. Ship something this week.
