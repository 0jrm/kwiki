---
name: wiki-update
description: >
  Sync the current project's knowledge into the Obsidian wiki. Use this skill from any project
  when the user says "update wiki", "sync to wiki", "save this to my wiki", "update obsidian",
  or wants to distill what they've been working on into their knowledge base. This is the
  cross-project skill that lets you push knowledge from wherever you are into the vault.
---

# Wiki Update — Sync Any Project to Your Wiki

You are distilling knowledge from the current project into the user's Obsidian wiki. This skill works from any project directory, not just the obsidian-wiki repo.

## Before You Start

1. Read `~/.obsidian-wiki/config` to get:
   - `OBSIDIAN_VAULT_PATH` — where the wiki lives
   - `OBSIDIAN_WIKI_REPO` — where the obsidian-wiki repo is cloned (for reading other skills if needed)
2. If `~/.obsidian-wiki/config` doesn't exist, tell the user to run `bash setup.sh` from their obsidian-wiki repo first.
3. Read `$OBSIDIAN_VAULT_PATH/.manifest.json` to check if this project has been synced before.
4. Read `$OBSIDIAN_VAULT_PATH/index.md` to know what the wiki already contains.

## Step 1: Understand the Project

Figure out what this project is by scanning the current working directory:

- `README.md`, docs/, any markdown files
- Source structure (frameworks, languages, key abstractions)
- `package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml` or whatever defines the project
- Git log (focus on commit messages that signal decisions, not "fix typo" stuff)
- Claude memory files if they exist (`.claude/` in the project)

Derive a clean project name from the directory name.

## Step 2: Compute the Delta

Check `.manifest.json` for this project:

- **First time?** Full scan. Everything is new.
- **Synced before?** Look at `last_commit_synced`. Only consider what changed since then. Use `git log <last_commit>..HEAD --oneline` to see what's new.

If nothing meaningful changed since last sync, tell the user and stop.

## Step 3: Decide What to Distill

This is the core question from Karpathy's pattern: **what would you want to know about this project if you came back in 3 months with zero context?**

Worth distilling:

- Architecture decisions and *why* they were made
- Patterns discovered while building (things you'd Google again otherwise)
- What tools, services, APIs the project depends on and how they're wired together
- Key abstractions, how they connect, what the mental model is
- Trade-offs that were evaluated, what was picked and why
- Things learned while building that aren't obvious from reading the code

Not worth distilling:

- File listings, boilerplate, config that's obvious
- Individual bug fixes with no broader lesson
- Dependency versions, lock file contents
- Implementation details the code already says clearly
- Routine changes anyone could read from the diff

The heuristic: **if reading the codebase answers the question, don't wiki it. If you'd have to re-derive the reasoning by reading git blame across 20 commits, wiki it.**

## Step 4: Distill into Wiki Pages

### Project-specific knowledge

Goes under `$VAULT/projects/<project-name>/`:

```
projects/<project-name>/
├── <project-name>.md          ← project overview (named after the project, NOT _project.md)
├── concepts/                  ← project-specific ideas, architectures
├── skills/                    ← project-specific how-tos, patterns
└── references/                ← project-specific source summaries
```

The overview page (`<project-name>.md`) should have:
- What the project is (one paragraph)
- Key concepts and how they connect
- Links to project-specific and global wiki pages

### Global knowledge

Things that aren't project-specific go in the global categories:

| What you found | Where it goes |
|---|---|
| A general concept learned | `concepts/` |
| A reusable pattern or technique | `skills/` |
| A tool/service/person | `entities/` |
| Cross-project analysis | `synthesis/` |

### Page format

Every page needs YAML frontmatter:

```markdown
---
title: >-
    Page Title
category: concepts
tags: [tag1, tag2]
sources: [projects/<project-name>]
summary: >-
    One or two sentences (≤200 chars) describing what this page covers.
provenance:
  extracted: 0.6
  inferred: 0.35
  ambiguous: 0.05
confidence: 0.8
sources_count: 1
last_confirmed: TIMESTAMP
decay_rate: "medium"
entities: []
quality: 0.85
created: TIMESTAMP
updated: TIMESTAMP
---

Use folded scalar syntax (summary: >-) for title and summary to keep frontmatter parser-safe across punctuation (:, #, quotes) without escaping rules.
Keep the title and summary contents indented by two spaces under summary: >-.

# Page Title

- A fact the codebase or a doc actually states.
- A reason the design works this way. ^[inferred]

Use [[wikilinks]] to connect to other pages.
```

**Write a `summary:` frontmatter field** on every new/updated page (1–2 sentences, ≤200 chars), using `>-` folded style. For project sync, a good summary answers "what does this page tell me about the project I wouldn't guess from its title?" This field powers cheap retrieval by `wiki-query`.

**Set confidence + decay fields** on every new/updated project page:
- `confidence`: default `0.8` for project pages synced from a live codebase you're actively working in. Lower if the page is heavily inferred or the project is exploratory.
- `sources_count`: count of commit ranges or referenced files contributing to this page. Start at `1`; increment when multiple sources contributed in this session.
- `last_confirmed`: set to current sync time.
- `decay_rate`: `"medium"` for most project pages. Use `"high"` if the page documents versions, dependencies, or current team structure.

**Apply provenance markers** per `llm-wiki` (Provenance Markers section). For project sync specifically:

- **Extracted** — anything visible in the code, config, or a doc/commit message: file structure, dependencies, function signatures, what a file does.
- **Inferred** — *why* a decision was made, design rationale, trade-offs, "the team chose X because Y" — unless a commit message, doc, or ADR states it explicitly.
- **Ambiguous** — when the code and docs disagree, or when there's clearly an in-progress migration with two patterns living side by side.

Compute the rough fractions and write the `provenance:` block on every new/updated page.

### Updating vs creating

- If a page already exists in the vault, **merge** new information into it. Don't create duplicates.
- If you're adding to an existing page, update the `updated` timestamp and add the new source.
- Check `index.md` to see what's already there before creating anything new.

## Step 5: Cross-link

After creating/updating pages:

- Add `[[wikilinks]]` from new pages to existing related pages
- Add `[[wikilinks]]` from existing pages back to the new ones where relevant
- Link the project overview to all project-specific pages and relevant global pages

## Step 6: Update Tracking

### Update `.manifest.json`

Add or update this project's entry:

```json
{
  "projects": {
    "<project-name>": {
      "source_cwd": "/absolute/path/to/project",
      "last_synced": "TIMESTAMP",
      "last_commit_synced": "abc123f",
      "pages_in_vault": ["projects/<project-name>/<project-name>.md", "..."]
    }
  }
}
```

### Update `index.md`

Add entries for any new pages created.

### Update `log.md`

Append:
```
- [TIMESTAMP] WIKI_UPDATE project=<project-name> pages_updated=X pages_created=Y source_cwd=/path/to/project
```

### Append to `_meta/audit.jsonl`

After writing the project page, append one entry per page written:
```json
{"ts":"<ISO8601-with-ms>","op":"update","skill":"wiki-update","page":"<vault-relative-path>","source":"<cwd-of-project>","action":"create","session":null}
```
Use `"action": "update"` if the page already existed. Create `_meta/` directory first if it doesn't exist.

## Quality Scoring

Every new or updated project page gets a `quality:` frontmatter field. Compute it using the same seven-signal heuristic defined in `wiki-ingest/SKILL.md` Step 5a. For project pages synced from an active codebase:

- Pages with a full README, multiple wikilinks, entities, and a good summary typically score ≥ 0.75.
- Use `quality: 0.85` as the example in the template (project pages tend to be well-sourced).
- Compute the actual value at write time; don't hardcode the example value.

## Quality Checklist

After syncing, verify:
- [ ] Project page exists at `projects/<project-name>/<project-name>.md`
- [ ] `index.md` and `log.md` updated
- [ ] `.manifest.json` updated with `last_commit_synced`
- [ ] Every new/updated page has a `summary:` frontmatter field (≤200 chars)
- [ ] Project page has `confidence`, `sources_count`, `last_confirmed`, `decay_rate` fields
- [ ] Project page has a `quality:` frontmatter field computed via the wiki-ingest heuristic
- [ ] Audit entries written to `_meta/audit.jsonl` for all pages created/updated

## Tips

- **Be aggressive about merging.** If the project uses React Server Components, don't create a new page if `concepts/react-server-components.md` already exists. Update the existing one and add this project as a source.
- **Consult the tag taxonomy.** Read `$VAULT/_meta/taxonomy.md` if it exists, and use canonical tags.
- **Don't copy code.** Distill the *knowledge*, not the implementation. "This project uses a debounced search pattern with 300ms delay" is useful. Pasting the actual debounce function is not.
- **Project overview is the anchor.** The `<project-name>.md` file is what you'd read to get oriented. Make it good.
