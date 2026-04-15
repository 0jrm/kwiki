---
name: wiki-sync
description: >
  Reconcile wiki state across multiple agents/workstations with deterministic,
  class-based conflict handling. Use when collaborative mode is enabled, before
  large write batches, after major write completion, or after rebuild operations.
---

# Wiki Sync — Multi-Agent Reconciliation

`wiki-sync` is an additive collaboration layer. If you never invoke it, existing single-agent workflows are unchanged.

## Goal

Reconcile local and peer wiki states safely, classify conflicts deterministically, auto-merge when safe, and emit explicit review queues when human resolution is required.

## Inputs

- `local_snapshot` (required): current vault state digest
- `peer_snapshot` (required): incoming vault state digest (remote/peer)
- `mode` (optional): `preflight` | `postwrite` | `rebuild-followup`
- `preserve_local_on_conflict` (optional, default `true`)

Snapshots should cover:
- markdown pages under category/project folders
- `_graph/entities.jsonl`, `_graph/edges.jsonl`
- `index.md`, `log.md`, `.manifest.json`
- optional `_meta/audit.jsonl` tail hash for provenance checks

## Conflict Classes (authoritative)

1. `non_overlapping`  
   Distinct files/pages changed on each side; safe auto-merge.
2. `same_page_non_overlapping_sections`  
   Same page changed but in different sections/blocks; merge with provenance note.
3. `same_claim_conflict`  
   Contradictory edits to the same entity/attribute claim; route to contradiction/supersession flow.
4. `structural_conflict`  
   Drift in `index.md`, `log.md`, `.manifest.json`, or incompatible `_graph`/audit states requiring explicit reconciliation.

## Reconciliation Flow

1. Compute file-level change sets (added/updated/deleted) for local and peer snapshots.
2. Classify each overlap using the 4-class model above.
3. Apply auto-merges for:
   - `non_overlapping`
   - `same_page_non_overlapping_sections` (with merge note)
4. For unresolved classes:
   - `same_claim_conflict`: emit review item with recommended supersession/ambiguity path
   - `structural_conflict`: stop auto-merge and emit explicit reconciliation checklist
5. Produce sync outcome:
   - `merged` (all safe merges applied)
   - `requires_review` (one or more unresolved conflicts)
   - `aborted` (validation failure or explicit stop)

## Safety Rules

- Never discard local content without explicit user approval.
- If safe reconciliation is not possible, preserve local writes and emit review instructions.
- No destructive operations are allowed as implicit sync side effects.

## Audit Logging

Every sync attempt appends one JSON line to `_meta/audit.jsonl`:

```json
{
  "ts": "2026-04-15T12:00:00.000Z",
  "op": "sync",
  "skill": "wiki-sync",
  "page": null,
  "source": "peer:vault-b",
  "action": "update",
  "session": null,
  "sync_outcome": "requires_review",
  "conflicts": {
    "non_overlapping": 3,
    "same_page_non_overlapping_sections": 1,
    "same_claim_conflict": 1,
    "structural_conflict": 0
  }
}
```

## Worked Example

Scenario:
- Agent A updates `projects/kwiki/kwiki.md` architecture section.
- Agent B updates the same page's deployment section and also changes a claim about retention thresholds.

Classification:
- Deployment + architecture edits: `same_page_non_overlapping_sections` -> auto-merge with provenance note.
- Retention threshold disagreement: `same_claim_conflict` -> route to supersession/ambiguity review queue.

Outcome:
- merged changes applied for non-overlapping sections
- one review item created for claim conflict
- final sync outcome: `requires_review`

## Quality Checklist

After each sync run:
- [ ] Change sets include pages, `_graph/*.jsonl`, `index.md`, `log.md`, `.manifest.json`
- [ ] Conflicts are classified only with the four canonical classes
- [ ] Local content is preserved when unresolved conflicts exist
- [ ] `_meta/audit.jsonl` has one append-only entry with outcome and class counts
