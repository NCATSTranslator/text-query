# translator-query — on-demand reference

Read this file only when a task needs the strategies or domain notes below. It is
kept out of `SKILL.md` so it is not loaded into context on every turn.

## Strategy 3: Multi-hop (3+ types) and gene networks

Chain `find-path` / `find-neighborhood` calls and intersect the node sets, or — if the logic gets complex — drop into Python with `TCT.format_query_json()` + `translator_query.parallel_api_query()` + `TCT.parse_KG()` (load resources once). Prefer chaining CLI calls first.

## Strategy 4: Detailed single-KP query (p-values, publications from one provider)

`find-neighborhood` already returns edges from every relevant KP (including the Microbiome KP) with their publications/p-values — the extractor surfaces them. To target **one** provider, query it directly. The Microbiome KP is in the catalog as `"Microbiome KP - TRAPI 1.5.0"`:
```
uv run tct query query-kp '<trapi_json>' "Microbiome KP - TRAPI 1.5.0" > /tmp/tq.json
```
The TRAPI JSON must use TCT's node/edge key shape (`n00`/`n01`, `e00`); build it with `TCT.format_query_json([curie], [], subject_categories, object_categories, predicates)` in a short Python snippet if hand-writing is error-prone. Microbiome KP endpoint: `https://multiomics.transltr.io/mbkp/query`.

## Domain Knowledge

- **Microbiome KP** connects OrganismTaxon to Gene, Disease, SmallMolecule, etc.; key metapaths are taxon↔disease and taxon↔gene.
- "Microbiome measurement" is a `biolink:PhenotypicFeature`, not a taxon.
- Microbiome KP uses specific NCBITaxon IDs (e.g. NCBITaxon:815 for Bacteroides), not general terms like "microbiome".
- ABCC11 = MRP8 (multidrug resistance-associated protein) — a pleiotropic efflux pump gene.
