# How Are Microbiome Communities in the Skin Affected by Changes in ABCC11?

**Query Date:** 2026-03-25
**Gene:** ABCC11 (NCBIGene:85320) — ATP-binding cassette subfamily C member 11 (MRP8)

---

## From Translator

### Direct ABCC11 → Organism Associations
**No microbial organisms** were found directly associated with ABCC11 across any Translator knowledge provider. The only organism edge was a trivial `biolink:in_taxon → Homo sapiens` from `infores:intact`.

### Microbiome KP Direct Query
The Microbiome KP (production: `multiomics.transltr.io/mbkp`) returned **0 edges** for ABCC11 in both directions (Gene→OrganismTaxon and OrganismTaxon→Gene).

### Path Finding (2-hop)
**No paths** were found connecting ABCC11 to any of five skin-associated microbes through Disease/Phenotype or Chemical intermediates:
- *Corynebacterium* (NCBITaxon:1716) — 0 paths
- *Staphylococcus* (NCBITaxon:1279) — 0 paths
- *Cutibacterium acnes* (NCBITaxon:1747) — 0 paths
- *Propionibacterium* (NCBITaxon:1743) — 0 paths
- *Malassezia* (NCBITaxon:55193) — 0 paths

### ABCC11 → Disease/Phenotype Associations
| Association | Predicate | Source |
|---|---|---|
| **EAR WAX, WET/DRY** (OMIM:117800) | `close_match`, `related_to` | `infores:omim`, `infores:clinvar` |
| **Axillary odor** (UMLS:C3149148) | `close_match` | `infores:omim` |
| **Colostrum secretion** (UMLS:C3149149) | `close_match` | `infores:omim` |
| Breast carcinoma (MONDO:0004989) | `phenotype_of` | `infores:hpo-annotations` |
| Neoplasm (MeSH:D009369) | `associated_with` | `infores:catrax-pharmacogenomics` |
| Leukopenia (MeSH:D007970) | `associated_with` | `infores:catrax-pharmacogenomics` |
| Disease Progression | `genetically_associated_with` | `infores:ctd` |
| Disease Exacerbation | `genetically_associated_with` | `infores:disgenet` |
| Ear malformation (MONDO:0007500) | `phenotype_of` | `infores:hpo-annotations` |

### ABCC11 → Chemical Associations (Transport Substrates)
| Chemical | Predicates | Sources |
|---|---|---|
| **Fluorouracil** | `interacts_with`, `affects`, `response_decreased_by` | `infores:drugcentral`, `infores:dgidb`, `infores:ctd`, `infores:text-mining-provider-targeted` |
| **Methotrexate** | `directly_physically_interacts_with`, `affects`, `response_decreased_by` | `infores:hetionet`, `infores:ctd`, `infores:hmdb` |
| **Folic acid** | `directly_physically_interacts_with` | `infores:hetionet`, `infores:hmdb` |
| **Probenecid** | `directly_physically_interacts_with` | `infores:hetionet`, `infores:hmdb` |
| **Pemetrexed** | `response_affected_by`, `affects`, `response_decreased_by` | `infores:ctd`, `infores:text-mining-provider-targeted` |

### Skin Disease → Microbe Associations (Independent Context)
While no path from ABCC11 was found, Translator does link skin conditions to microbes independently:

**Acne** (MONDO:0011438):
| Microbe | Predicate | Source |
|---|---|---|
| *Cutibacterium acnes* | `causes`, `related_to` | `infores:robokop`, `infores:semmeddb` |
| *Propionibacterium* | `causes`, `related_to` | `infores:robokop`, `infores:semmeddb` |
| *Staphylococcus aureus* | `causes` | `infores:robokop` |
| *Staphylococcus epidermidis* | `causes`, `related_to` | `infores:robokop`, `infores:semmeddb` |

**Dermatitis** (MONDO:0002406):
| Microbe | Predicate | Source |
|---|---|---|
| *Staphylococcus aureus* | `related_to` | `infores:semmeddb` |
| Probiotics | `related_to` | `infores:semmeddb` |

---

## Additional Biological Context (LLM Knowledge)

*The following comes from my training knowledge, not from Translator queries:*

ABCC11 encodes the MRP8 efflux transporter, expressed in apocrine glands, ceruminous glands, and mammary tissue. The well-characterized SNP **rs17822931 (538G>A)** causes a loss-of-function variant that determines:

1. **Ear wax type** — wet (G allele, functional) vs. dry (A allele, loss-of-function). The dry type is nearly universal in East Asian populations (~80-95%) and rare in European/African populations (~0-3%).

2. **Axillary odor and skin microbiome** — Functional ABCC11 secretes odor precursors (3-methyl-2-hexenoic acid, 3-hydroxy-3-methylhexanoic acid, androsterone sulfate conjugates) into the apocrine gland lumen. These precursors are **odorless** until metabolized by axillary bacteria:
   - ***Corynebacterium*** spp. (*C. striatum*, *C. jeikeium*) — primary converters of glutamine conjugates to volatile thioalcohols responsible for body odor
   - ***Staphylococcus*** spp. (*S. hominis*, *S. haemolyticus*) — convert branched-chain amino acid conjugates

3. **Mechanism of microbiome impact:** In individuals homozygous for the loss-of-function allele (AA genotype):
   - Apocrine glands secrete **fewer lipid-based substrates** into the axillary skin environment
   - This alters the **nutrient landscape** available to skin-resident bacteria
   - Studies (e.g., Prokop-Prigge et al., 2016, *Journal of Investigative Dermatology*) show that ABCC11 genotype correlates with differences in axillary bacterial community composition
   - AA individuals tend to have lower *Corynebacterium* abundance and higher *Staphylococcus* abundance, reflecting reduced availability of Corynebacterium-preferred substrates
   - This represents one of the clearest known examples of a human gene influencing commensal microbe composition via substrate availability

---

## Knowledge Gaps in Translator

### Gap 1: ABCC11 → Apocrine Secretion Composition
**Missing edge:** `ABCC11 → biolink:affects → apocrine gland secretion` or specific metabolites
- **Why it matters:** This is the primary mechanism by which ABCC11 variants influence skin microbiomes
- **Potential data sources:** GWAS Catalog (rs17822931 associations), ClinVar functional annotations, metabolomics studies
- **Suggested edge type:** `biolink:Gene → biolink:affects → biolink:BiologicalProcess` or `biolink:ChemicalEntity`

### Gap 2: Apocrine Metabolites → Skin Microbe Abundance
**Missing edge:** e.g., `3-methyl-2-hexenoic acid → biolink:substrate_for → Corynebacterium`
- **Why it matters:** The causal chain from gene → secretion → microbe depends on metabolite-microbe substrate relationships
- **Potential data sources:** MetaCyc, KEGG, published skin metabolomics studies
- **Suggested edge type:** `biolink:SmallMolecule → biolink:interacts_with → biolink:OrganismTaxon`

### Gap 3: ABCC11 Genotype → Skin Microbiome Composition
**Missing edge:** `ABCC11 → biolink:correlated_with → Corynebacterium` (or Staphylococcus)
- **Why it matters:** Direct genotype-microbiome association data exists in published literature but is not in Translator
- **Potential data sources:** Prokop-Prigge et al. (2016), skin metagenomics GWAS, Human Microbiome Project skin site data
- **Suggested KP:** Microbiome KP could ingest genotype-stratified 16S/shotgun metagenomics studies from skin sites

### Gap 4: Axillary Odor / Body Odor → Microbiome
**Missing edge:** `Body odor (HP:0500001) → biolink:related_to → Corynebacterium/Staphylococcus`
- **Why it matters:** Body odor is directly microbe-mediated. Translator returned 0 organism associations for "Body Odor" (HP:0500001).
- **Potential data sources:** Text mining of dermatology/microbiology literature, SemMedDB

### Gap 5: Missing 2-hop Bridging
**No paths found** from ABCC11 → Disease → Skin Microbe, despite both sides existing independently in Translator. The diseases associated with ABCC11 (ear wax, axillary odor) lack microbe edges, and the microbes associated with skin conditions (acne, dermatitis) lack ABCC11 edges. Bridging data linking cerumen type / axillary phenotypes to specific microbial taxa would close these paths.

---

## Query Methods Used

- **Neighborhood Search:** ABCC11 → OrganismTaxon (1 trivial result)
- **Neighborhood Search:** ABCC11 → Disease/PhenotypicFeature (14 associations)
- **Neighborhood Search:** ABCC11 → ChemicalEntity/SmallMolecule (20+ associations)
- **Neighborhood Search:** Acne → OrganismTaxon (52 associations, 4 skin microbes)
- **Neighborhood Search:** Dermatitis → OrganismTaxon (34 associations)
- **Direct TRAPI:** Microbiome KP — 0 edges both directions
- **Path_finder:** ABCC11 ↔ 5 skin microbes through Disease/Phenotype — 0 paths
- **Path_finder:** ABCC11 ↔ 5 skin microbes through Chemical — 0 paths

## APIs Queried Successfully

Automat-robokop, Automat-ctd, Automat-hetionet, Automat-cam-kp, Automat-pharos, Automat-ubergraph, Automat-monarchinitiative, RTX KG2, CATRAX BigGIM DrugResponse KP, CATRAX Pharmacogenomics KP, BioThings Explorer, Service Provider TRAPI, Microbiome KP, Text Mined Cooccurrence API
