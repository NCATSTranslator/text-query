---
name: explore-connections
description: Find how two biomedical entities are connected through intermediate nodes using Translator. Takes two entity names and an optional intermediate type.
argument-hint: [entity1, entity2, intermediate type]
disable-model-invocation: true
---

Find paths connecting two biomedical entities through intermediate nodes using TCT's Path_finder.

Parse `$ARGUMENTS` as comma-separated values: entity1, entity2, and optionally an intermediate type (defaults to genes/proteins if not specified).

## Category mapping for intermediate type

| User says | Biolink categories |
|---|---|
| genes, proteins | `['biolink:Gene', 'biolink:Protein']` |
| microbes, organisms | `['biolink:OrganismTaxon']` |
| diseases | `['biolink:Disease']` |
| drugs, chemicals | `['biolink:Drug', 'biolink:SmallMolecule', 'biolink:ChemicalEntity']` |
| phenotypes | `['biolink:PhenotypicFeature']` |
| cells | `['biolink:Cell']` |

## Script to write and execute

Write a Python script and run it via `uv run python3 <script>`:

```python
import matplotlib
matplotlib.use('Agg')
from TCT import name_resolver, translator_metakg, TCT

# Load resources
APInames, metaKG, _ = translator_metakg.load_translator_resources()
API_predicates = {api: list(set(metaKG[metaKG['API'] == api]['Predicate'])) for api in set(metaKG['API'])}

# Resolve entities (use only_taxa for genes)
entity1 = name_resolver.lookup("<entity1_name>")  # add gene hints if appropriate
entity2 = name_resolver.lookup("<entity2_name>")
print(f"Entity 1: {entity1.label} ({entity1.curie})")
print(f"Entity 2: {entity2.label} ({entity2.curie})")

# Find paths
intermediate_categories = [...]  # from mapping above
paths, node1_id, node2_id, r1, r2, p1, p2, rank1, rank2 = TCT.Path_finder(
    entity1.curie, entity2.curie,
    intermediate_categories,
    APInames, metaKG, API_predicates)

print(f"\nFound {len(paths)} connecting entities")
print(paths.head(20).to_string())
```

## Extracting edge provenance

Path_finder returns `r1`, `r2` (raw results) and `p1`, `p2` (parsed results). Use the parsed results to extract provenance for each hop:

```python
# After Path_finder, extract provenance for each path
for idx, row in paths.head(10).iterrows():
    intermediate = row['output_node']
    print(f"\nPath via {row['output_node_name']} ({intermediate}):")
    print(f"  Hop 1: {entity1.label} --[{row['predictes1']}]--> {row['output_node_name']}")
    # Look up edge in p1 (result_parsed for entity1 side)
    for key in [f"{entity1.curie}_{intermediate}", f"{intermediate}_{entity1.curie}"]:
        if key in p1:
            print(f"    Sources: {list(set(p1[key]['primary_knowledge_source']))}")
    print(f"  Hop 2: {row['output_node_name']} --[{row['predictes2']}]--> {entity2.label}")
    for key in [f"{entity2.curie}_{intermediate}", f"{intermediate}_{entity2.curie}"]:
        if key in p2:
            print(f"    Sources: {list(set(p2[key]['primary_knowledge_source']))}")
```

## Presenting results

- The `paths` DataFrame columns: `score`, `output_node`, `predictes1` (entity1→intermediate predicates), `predictes2` (entity2→intermediate predicates), `output_node_name`
- Higher score = more knowledge sources support this path
- **For each path, include the primary knowledge sources (infores IDs) for both hops**
- Explain the top paths in biological terms: "Entity1 --[predicate1]--> Intermediate --[predicate2]--> Entity2"
- Clearly label any biological interpretation beyond the returned predicates as "LLM knowledge" — and note what Translator edges would be needed to close the gap
- Offer to dig deeper into any specific intermediate node
