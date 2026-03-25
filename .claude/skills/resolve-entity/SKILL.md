---
name: resolve-entity
description: Look up a biomedical entity (gene, disease, microbe, drug) in Translator to find its CURIE identifier, type, and synonyms
argument-hint: [entity name]
disable-model-invocation: true
---

Resolve the biomedical entity "$ARGUMENTS" to its Translator identifier using TCT's name resolver.

Write and execute a Python script via `uv run python3 <script>` that does the following:

```python
import matplotlib
matplotlib.use('Agg')
from TCT import name_resolver, node_normalizer

name = "$ARGUMENTS"

# Try lookup with multiple results for disambiguation
results = name_resolver.lookup(name, return_top_response=False, limit=5)

for i, node in enumerate(results):
    prefix = ">>>" if i == 0 else "   "
    print(f"{prefix} {node.label} ({node.curie})")
    # Show only the primary biolink types (filter out generic ones)
    primary_types = [t for t in node.types if t.startswith('biolink:') and t not in [
        'biolink:NamedThing', 'biolink:Entity', 'biolink:BiologicalEntity',
        'biolink:ThingWithTaxon', 'biolink:PhysicalEssence', 'biolink:OntologyClass',
        'biolink:PhysicalEssenceOrOccurrent']]
    print(f"    Types: {', '.join(primary_types[:5])}")
    if hasattr(node, 'taxa') and node.taxa:
        print(f"    Taxa: {node.taxa}")
```

If the name looks like a gene, also try with `only_taxa='NCBITaxon:9606'` and `biolink_type='biolink:Gene'` to get the human gene specifically.

Present the results clearly:
- Highlight the top match
- Show alternatives if the name is ambiguous
- Explain what the CURIE prefix means (e.g., NCBIGene = NCBI Gene ID, MONDO = Monarch Disease Ontology, NCBITaxon = NCBI Taxonomy)
