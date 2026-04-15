# Ingest Prompt Templates

These are the mental frameworks to use when distilling a source into wiki pages.

## Knowledge Extraction Frame

When reading a source document, ask yourself:

1. **What are the 3-5 most important ideas in this document?**
   These become concepts pages or updates to existing concept pages.

2. **Who or what is mentioned that deserves its own page?**
   People, tools, organizations, projects → entity pages.

3. **What does this document teach you how to do?**
   Procedures, workflows, techniques → skills pages.

4. **What claims does this document make?**
   Each claim needs a source attribution. If it contradicts an existing wiki claim, note the contradiction.

5. **How does this connect to what the wiki already knows?**
   This is the most important question. The value of the wiki compounds through connections.

## Synthesis Frame

When a new source covers ground that existing pages already cover:

- Don't duplicate — synthesize
- If the new source agrees with existing content, strengthen the claims with additional attribution
- If it disagrees, create an "Open Questions" or "Debate" section noting both positions
- If it adds nuance, weave it into the existing narrative

## Cross-Reference Discovery

After extracting knowledge, look for these connection patterns:

- **Is-a**: "Transformers are a type of neural network" → link from transformer page to neural-network page
- **Uses**: "RLHF uses reward models" → link from RLHF to reward-models
- **Contrasts-with**: "CNNs vs. Transformers for vision" → mutual links
- **Part-of**: "Attention is a component of transformers" → link from attention to transformers
- **Created-by**: "Transformers were introduced by Vaswani et al." → link to entity page
- **Applied-in**: "Transformers are used in GPT" → link from transformers to GPT

## LaTeX and BibTeX sources

Use these frames when the source corpus includes `.tex` or `.bib` files:

- **BibTeX entry typing**: map `@article`, `@inproceedings`, `@book`, `@misc`, and `@techreport` into entity/reference-oriented wiki targets; preserve each cite key for traceability.
- **Field extraction**: treat `title`, `author`, `year`, `journal`/`booktitle`, and `doi`/`url` as extracted claims; avoid dumping full entry blobs unless needed.
- **LaTeX claim extraction**: prioritize definitions, theorems, assumptions, and explicitly stated conclusions; convert notation-heavy passages into plain-language claims.
- **Math paraphrase provenance**: when translating notation into prose, mark the paraphrased claim with `^[inferred]` unless the exact wording appears in the source.
- **Citation alignment**: map `\cite{foo}` mentions to the same wiki target that would be produced from BibTeX key `foo` so links converge across `.tex` and `.bib` ingests.
- **Preamble/macro bias**: deprioritize long preambles, style directives, and macro scaffolding unless they encode reusable conceptual meaning.
