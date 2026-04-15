---
name: data-ingest
description: >
  Ingest any raw text data, conversation logs, chat exports, or unstructured documents into the Obsidian wiki.
  Use this skill when the user wants to process data that isn't standard documents or Claude history —
  things like ChatGPT exports, Slack threads, Discord logs, meeting transcripts, journal entries, CSV data,
  browser bookmarks, email archives, or any raw text dump. Triggers on "ingest this data", "process these logs",
  "add this export to the wiki", "import my chat history from X". This is the catch-all for any text source
  not covered by the more specific ingest skills.
---

# Data Ingest — Universal Text Source Handler

You are ingesting arbitrary text data into an Obsidian wiki. The source could be anything — conversation exports, log files, transcripts, data dumps. Your job is to figure out the format, extract knowledge, and distill it into wiki pages.

## Before You Start

1. Read `.env` to get `OBSIDIAN_VAULT_PATH`
2. Read `.manifest.json` at the vault root — check if this source has been ingested before
3. Read `index.md` at the vault root to know what already exists

If the source path is already in `.manifest.json` and the file hasn't been modified since `ingested_at`, tell the user it's already been ingested. Ask if they want to re-ingest anyway.

## PII Filter

Apply this filter to all raw source text before extracting knowledge, regardless of format. Data exports, chat logs, and CSV dumps are particularly high-risk — they often contain credentials from API integrations or copied `.env` values.

**Always redact (context-independent):**
- OpenAI/Anthropic keys: `sk-[A-Za-z0-9]{20,}` → `[REDACTED:api-key]`
- GitHub tokens: `ghp_[A-Za-z0-9]{36}` or `ghs_[A-Za-z0-9]{36}` → `[REDACTED:github-token]`
- AWS access keys: `AKIA[A-Z0-9]{16}` → `[REDACTED:aws-key]`
- Slack tokens: `xoxb-[A-Za-z0-9-]+` or `xoxp-[A-Za-z0-9-]+` → `[REDACTED:slack-token]`
- Bearer tokens in headers: `Bearer [A-Za-z0-9._\-]{20,}` → `[REDACTED:bearer-token]`
- Private key blocks: `-----BEGIN ... PRIVATE KEY-----` through `-----END ... PRIVATE KEY-----` → `[REDACTED:private-key]`
- JWT tokens: strings matching `eyJ[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+` → `[REDACTED:jwt-token]`

**Redact in credential context** (inside `.env` files, config blocks, JSON auth responses):
- Email addresses found alongside API credentials or auth config → `[REDACTED:email]`

**Never redact:**
- Email addresses that are the subject of knowledge distillation (e.g. a page about email deliverability can contain example addresses)
- Hashes, IDs, or opaque strings that are not in a credential-looking context
- Content already labeled `[REDACTED:*]` from a prior pass

**On detection:** Replace the matched text inline with `[REDACTED:pattern-name]`. Append a warning to the ingest summary: `"PII filter: redacted N occurrences (pattern-name, ...)"` — but do **not** abort the ingest. Redact and continue.

## Step 1: Identify the Source Format

Read the file(s) the user points you at. Common formats you'll encounter:

| Format | How to identify | How to read |
|---|---|---|
| **JSON / JSONL** | `.json` / `.jsonl` extension, starts with `{` or `[` | Parse with Read tool, look for message/content fields |
| **Markdown** | `.md` extension | Read directly |
| **Plain text** | `.txt` extension or no extension | Read directly |
| **CSV / TSV** | `.csv` / `.tsv`, comma or tab separated | Parse rows, identify columns |
| **HTML** | `.html`, starts with `<` | Extract text content, ignore markup |
| **Chat export** | Varies — look for turn-taking patterns (user/assistant, human/ai, timestamps) | Extract the dialogue turns |
| **Images** | `.png` / `.jpg` / `.jpeg` / `.webp` / `.gif` | *Requires a vision-capable model.* Use the Read tool — it renders images into your context. Screenshots, whiteboards, diagrams all qualify. Models without vision support should skip and report which files were skipped. |

### Common Chat Export Formats

**ChatGPT export** (`conversations.json`):
```json
[{"title": "...", "mapping": {"node-id": {"message": {"role": "user", "content": {"parts": ["text"]}}}}}]
```

**Slack export** (directory of JSON files per channel):
```json
[{"user": "U123", "text": "message", "ts": "1234567890.123456"}]
```

**Generic chat log** (timestamped text):
```
[2024-03-15 10:30] User: message here
[2024-03-15 10:31] Bot: response here
```

Don't try to handle every format upfront — read the actual data, figure out the structure, and adapt.

### Images and visual sources

When the user dumps a folder of screenshots, whiteboard photos, or diagram exports, treat each image as a source:

- Use the Read tool on the image path — it will render the image into context.
- **Transcribe** any visible text verbatim (this is the only extracted content from an image).
- **Describe** structure: for diagrams, list nodes/edges; for screenshots, name the app and what's on screen.
- **Extract** the concepts the image conveys — what's it *about*? Most of this is `^[inferred]`.
- **Flag** anything you can't read, can't identify, or are guessing at with `^[ambiguous]`.

Image-derived pages will skew heavily inferred — that's expected and the provenance markers will reflect it. Set `source_type: "image"` in the manifest entry. Skip files with EXIF-only changes (re-saved with no visual diff) — compare via the standard delta logic.

For folders of mixed images (e.g. a screenshot timeline of a debugging session), cluster by visible topic rather than per-file. Twenty screenshots of the same UI bug should produce one wiki page, not twenty.

## Step 2: Extract Knowledge

Regardless of format, extract the same things:

- **Topics** discussed — what subjects come up?
- **Decisions** made — what was concluded or decided?
- **Facts** learned — what concrete information is stated?
- **Procedures** described — how-to knowledge, workflows, steps
- **Entities** mentioned — people, tools, projects, organizations
- **Connections** — how do topics relate to each other and to existing wiki content?

### For conversation data specifically:

Focus on the **substance**, not the dialogue. A 50-message debugging session might yield one skills page about the fix. A long brainstorming chat might yield three concept pages.

Skip:
- Greetings, pleasantries, meta-conversation ("can you help me with...")
- Repetitive back-and-forth that doesn't add new information
- Raw code dumps (unless they illustrate a reusable pattern)

## Step 3: Cluster and Deduplicate

Before creating pages:
- Group extracted knowledge by topic (not by source file or conversation)
- Check existing wiki pages — does this knowledge belong on an existing page?
- Merge overlapping information from multiple sources
- Note contradictions between sources

## Step 4: Distill into Wiki Pages

Follow the `wiki-ingest` skill's process for creating/updating pages:

- Use correct category directories (`concepts/`, `entities/`, `skills/`, etc.)
- Add YAML frontmatter with title, category, tags, sources
- Use `[[wikilinks]]` to connect to existing pages
- Attribute claims to their source
- **Write a `summary:` frontmatter field** on every new page (1–2 sentences, ≤200 characters) answering "what is this page about?" — this is what downstream skills read to avoid opening the page body.
- **Apply provenance markers** per the convention in `llm-wiki`. Conversation, log, and chat data tend to be high-inference — you're often reading between the turns to extract a coherent claim. Be liberal with `^[inferred]` for synthesized patterns and with `^[ambiguous]` when speakers contradict each other or you're unsure who's right. Write a `provenance:` frontmatter block on each new/updated page.

## Step 5: Update Manifest and Special Files

**`.manifest.json`** — Add an entry for each source file processed:
```json
{
  "ingested_at": "TIMESTAMP",
  "size_bytes": FILE_SIZE,
  "modified_at": FILE_MTIME,
  "source_type": "data",  // or "image" for png/jpg/webp/gif sources
  "project": "project-name-or-null",
  "pages_created": ["list/of/pages.md"],
  "pages_updated": ["list/of/pages.md"]
}
```

**`index.md`** and **`log.md`**:
```
- [TIMESTAMP] DATA_INGEST source="path/to/data" format=FORMAT pages_updated=X pages_created=Y
```

**`_meta/audit.jsonl`** — After each page write (one entry per page, inside any write loop):
```json
{"ts":"<ISO8601-with-ms>","op":"ingest","skill":"data-ingest","page":"<vault-relative-path>","source":"<source-path>","action":"create","session":null}
```
Use `"action": "update"` if the page already existed. Create `_meta/` directory first if it doesn't exist.

## Quality Checklist

After ingesting, verify:
- [ ] Every new page has frontmatter with title, category, tags, sources
- [ ] `index.md` and `log.md` updated
- [ ] Source attribution present for every claim
- [ ] PII filter ran on source content; any redactions noted in summary
- [ ] Audit entries written to `_meta/audit.jsonl` for all pages created/updated

## Tips

- **When in doubt about format, just read it.** The Read tool will show you what you're dealing with.
- **Large files:** Read in chunks using offset/limit. Don't try to load a 10MB JSON in one go.
- **Multiple files:** Process them in order, building up wiki pages incrementally.
- **Binary files:** Skip them, *except* images — those are first-class sources via the Read tool's vision support.
- **Encoding issues:** If you see garbled text, mention it to the user and move on.
