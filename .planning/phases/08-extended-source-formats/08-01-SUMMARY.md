---
subsystem: ingest-source-formats
provides: [latex-bibtex-ingest, structured-text-ingest, status-scan-parity]
requires: [schema-and-migration-governance]
affects: [wiki-ingest, wiki-status, data-ingest, onboarding-docs]
---

# Phase 08-01 Summary

Implemented Phase 8 extension coverage across ingest and onboarding docs with a single canonical extension catalog anchored in `wiki-ingest`.

## Completed Changes

- Expanded `wiki-ingest` Step 1 supported formats to include LaTeX/BibTeX (`.tex`, `.ltx`, `.sty`, `.cls`, `.bib`, `.bst`), structured text (`.yaml`, `.yml`, `.toml`, `.json`, `.json5`, `.xml`), and documentation markup (`.rst`, `.adoc`, `.asciidoc`, `.org`).
- Added concise per-format distillation guidance in `wiki-ingest` for LaTeX, BibTeX, and YAML/TOML handling.
- Reinforced PII guidance in `wiki-ingest` and `data-ingest` for YAML/TOML secret-bearing keys and values.
- Added a concise "LaTeX and BibTeX sources" extraction frame to `wiki-ingest/references/ingest-prompts.md`.
- Updated `data-ingest` format identification table to include YAML/TOML and LaTeX/BibTeX rows with consistent handling language.
- Updated `wiki-status` document scan instructions to mirror the `wiki-ingest` extension set, explicitly exclude junk directories, and report zero-match source directories.
- Updated architecture/onboarding docs (`llm-wiki`, `README`, `SETUP`) to reflect expanded source coverage and point to `wiki-ingest` as the canonical list.

## Compatibility and Risk Notes

- Backward compatibility preserved: no manifest schema changes and no new required `source_type` values.
- No new dependencies added; all parsing remains text-first and agent-native.
- Source-format expansion is additive and does not alter existing skip/hash behavior.
