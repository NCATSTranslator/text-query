# Neuroinflammation → Impaired Learning and Memory

*Query run: 2026-03-25 11:33*

**Original query:** How does neuroinflammation lead to impaired learning and memory?

---

## Entity Resolution

| Query | Resolved Label | CURIE | Type |
|---|---|---|---|
| Neuroinflammation | Neuroinflammation | HP:0033429 | PhenotypicFeature |
| Memory impairment | Short term memory impairment | HP:0033687 | PhenotypicFeature |
| Learning disability | learning disability | MONDO:0004681 | Disease |

## Genes/Proteins Associated with Neuroinflammation

| CURIE | Name | Knowledge Sources | Predicates |
|---|---|---|---|
| NCBIGene:8517 | **IKBKG** | 1 | has_phenotype |
| NCBIGene:51284 | **TLR7** | 1 | has_phenotype |
| NCBIGene:4538 | **ND4** | 1 | related_to |
| NCBIGene:7097 | **TLR2** | 1 | affects |
| NCBIGene:969 | **CD69** | 1 | affects |
| NCBIGene:706 | **TSPO** | 1 | affects |
| NCBIGene:3605 | **IL17A** | 1 | affects |
| UniProtKB:Q5CZI7 | **MAPT protein, human** | 1 | affects |
| NCBIGene:114548 | **NLRP3** | 1 | affects |
| NCBIGene:1269 | **CNR2** | 1 | affects |
| NCBIGene:7099 | **TLR4** | 1 | affects |
| NCBIGene:54209 | **TREM2** | 1 | affects |
| NCBIGene:3934 | **LCN2** | 1 | affects |
| NCBIGene:9692 | **PRORP** | 1 | has_phenotype |

## Path Finding: Neuroinflammation → Gene/Protein → Memory Impairment

No direct paths found between `HP:0033429` and `HP:0033687` through genes/proteins.

> **Note:** The resolver mapped "memory impairment" to the specific term **"Short term memory impairment"** (HP:0033687), which may be too narrow. Consider querying with a broader term like "cognitive impairment".


## Path Finding: Neuroinflammation → Gene/Protein → Learning Disability

| Score | Gene/Protein | Predicate (neuro→gene) | Predicate (gene→learning) |
|---|---|---|---|
| 1.0 | **TLR4** (NCBIGene:7099) | affects | genetically_associated_with; gene_associated_with_condition |
| 0.5 | **Genes** (UMLS:C0017337) | affects | affects |

---

## Biological Interpretation

The strongest supported mechanistic path (score 1.0):

```
Neuroinflammation --[affects]--> TLR4 --[genetically_associated_with / gene_associated_with_condition]--> Learning Disability
```

Neuroinflammation impairs learning and memory through several convergent mechanisms:

1. **NLRP3 inflammasome activation** → IL-1β/IL-18 release → synaptic depression in hippocampus
2. **TLR4 signaling** → NF-κB activation → pro-inflammatory gene cascade → LTP suppression → learning deficits
3. **TREM2/microglial dysregulation** → excessive synapse pruning → memory circuit disruption
4. **MAPT/Tau hyperphosphorylation** → neurofibrillary tangles → hippocampal neuron loss
5. **IL17A / BBB disruption** → peripheral immune cell infiltration → chronic neuronal stress
