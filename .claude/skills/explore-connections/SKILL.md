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

## Presenting results

- The `paths` DataFrame columns: `score`, `output_node`, `predictes1` (entity1→intermediate predicates), `predictes2` (entity2→intermediate predicates), `output_node_name`
- Higher score = more knowledge sources support this path
- Explain the top paths in biological terms: "Entity1 --[predicate1]--> Intermediate --[predicate2]--> Entity2"
- Offer to dig deeper into any specific intermediate node
