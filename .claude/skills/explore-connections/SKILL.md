---
name: explore-connections
description: Find how two biomedical entities are connected through intermediate nodes using Translator. Takes two entity names and an optional intermediate type.
argument-hint: [entity1, entity2, intermediate type]
disable-model-invocation: true
---

Find paths connecting two biomedical entities through an intermediate node type, using the **TCT (Translator Component Toolkit)** `tct` CLI. No Python needed.

Parse `$ARGUMENTS` as comma-separated values: `entity1`, `entity2`, and optionally an intermediate type (defaults to genes/proteins if not given).

## Category mapping for the intermediate type

Pass the chosen list as the JSON `INTERMEDIATE_CATEGORIES` argument to `find-path`:

| User says | Biolink categories |
|---|---|
| genes, proteins | `["biolink:Gene", "biolink:Protein"]` |
| microbes, organisms | `["biolink:OrganismTaxon"]` |
| diseases | `["biolink:Disease"]` |
| drugs, chemicals | `["biolink:Drug", "biolink:SmallMolecule", "biolink:ChemicalEntity"]` |
| phenotypes | `["biolink:PhenotypicFeature"]` |
| cells | `["biolink:Cell"]` |

## Step 1 — resolve both entities

Use the CLI. Pass `--biolink-type` (and `--only-taxa "NCBITaxon:9606"` for human genes) so you get the right-typed CURIE — a wrong-typed CURIE returns no paths:
```
uv run tct name lookup-name "<entity1>" --biolink-type "<type>"
uv run tct name lookup-name "<entity2>" --biolink-type "<type>"
```
Read the `curie` from each result.

## Step 2 — find the paths

`find-path` queries and ranks bridging nodes across all relevant KPs in one call. It prints a full TRAPI message, so redirect to a file and summarize with the bundled extractor instead of reading the raw JSON:
```
uv run tct query find-path "<curie1>" "<curie2>" '["biolink:OrganismTaxon"]' > /tmp/ec.json
uv run python3 .claude/skills/translator-query/extract_trapi.py /tmp/ec.json 20
```
The extractor prints each bridging node with its score, predicates, primary knowledge sources (infores IDs), and supporting publications. Add `--scoring-method edges` to score by edge count instead of distinct infores (default `infores`).

## Presenting results

- Each row is an intermediate node connecting entity1 and entity2; higher score = more shared support.
- For each top path, state it as "Entity1 → Intermediate → Entity2" and cite the predicates and primary knowledge sources (infores IDs) the extractor reported.
- Explain predicates in plain language (e.g. `biolink:occurs_together_in_literature_with` = "co-mentioned in the literature").
- Clearly label any biological interpretation beyond the returned edges as "LLM knowledge", and note which Translator edge would be needed to close the gap.
- Offer to dig deeper into any specific intermediate node (e.g. run `/translator-query` for its neighborhood).
