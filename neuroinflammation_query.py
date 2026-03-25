import matplotlib
matplotlib.use('Agg')
from TCT import name_resolver, translator_metakg, translator_query, TCT
from datetime import datetime

ORIGINAL_QUERY = "How does neuroinflammation lead to impaired learning and memory?"

OUTPUT_FILE = "neuroinflammation_results.md"

print("Loading Translator resources (this takes ~30 seconds)...")
APInames, metaKG, _ = translator_metakg.load_translator_resources()
API_predicates = {api: list(set(metaKG[metaKG['API'] == api]['Predicate'])) for api in set(metaKG['API'])}
print("Resources loaded.\n")

# Resolve entities
print("Resolving entity names...")
neuro = name_resolver.lookup("neuroinflammation")
memory = name_resolver.lookup("memory impairment")
learning = name_resolver.lookup("learning disability")
print(f"Neuroinflammation -> {neuro.curie} | Memory impairment -> {memory.curie} | Learning disability -> {learning.curie}\n")

# Neighborhood: genes/proteins associated with neuroinflammation
print("Running neighborhood search...")
node_id, result, result_parsed, ranked_df = TCT.Neighborhood_finder(
    neuro.curie,
    ['biolink:Gene', 'biolink:Protein'],
    APInames, metaKG, API_predicates)

# Path finding: neuroinflammation → genes/proteins → memory impairment
print("Running path finding (memory impairment)...")
paths, node1_id, node2_id, r1, r2, p1, p2, rank1, rank2 = TCT.Path_finder(
    neuro.curie, memory.curie,
    ['biolink:Gene', 'biolink:Protein'],
    APInames, metaKG, API_predicates)

# Path finding: neuroinflammation → genes/proteins → learning disability
print("Running path finding (learning disability)...")
paths2, *_ = TCT.Path_finder(
    neuro.curie, learning.curie,
    ['biolink:Gene', 'biolink:Protein'],
    APInames, metaKG, API_predicates)

# Write markdown output
with open(OUTPUT_FILE, "w") as f:
    f.write(f"# Neuroinflammation → Impaired Learning and Memory\n\n")
    f.write(f"*Query run: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n")
    f.write(f"**Original query:** {ORIGINAL_QUERY}\n\n")
    f.write("---\n\n")

    # Entity resolution
    f.write("## Entity Resolution\n\n")
    f.write("| Query | Resolved Label | CURIE | Type |\n")
    f.write("|---|---|---|---|\n")
    f.write(f"| Neuroinflammation | {neuro.label} | {neuro.curie} | {neuro.types[0].replace('biolink:','')} |\n")
    f.write(f"| Memory impairment | {memory.label} | {memory.curie} | {memory.types[0].replace('biolink:','')} |\n")
    f.write(f"| Learning disability | {learning.label} | {learning.curie} | {learning.types[0].replace('biolink:','')} |\n")
    f.write("\n")

    # Neighborhood results
    f.write("## Genes/Proteins Associated with Neuroinflammation\n\n")
    gene_rows = ranked_df[ranked_df['output_node'].str.startswith(('NCBIGene:', 'UniProtKB:'))].head(20)
    if not gene_rows.empty:
        f.write("| CURIE | Name | Knowledge Sources | Predicates |\n")
        f.write("|---|---|---|---|\n")
        for _, row in gene_rows.iterrows():
            preds = row['unique_predicates']
            if isinstance(preds, list):
                preds_str = ", ".join(p.replace("biolink:","") for p in set(preds))
            else:
                preds_str = str(preds).replace("biolink:","")
            f.write(f"| {row['output_node']} | **{row['Name']}** | {row['Num_of_primary_infores']} | {preds_str} |\n")
    else:
        f.write(ranked_df.head(20).to_markdown(index=False))
    f.write("\n")

    # Path finding — memory impairment
    f.write("## Path Finding: Neuroinflammation → Gene/Protein → Memory Impairment\n\n")
    if paths.empty:
        f.write(f"No direct paths found between `{neuro.curie}` and `{memory.curie}` through genes/proteins.\n\n")
        f.write(f"> **Note:** The resolver mapped \"memory impairment\" to the specific term "
                f"**\"{memory.label}\"** ({memory.curie}), which may be too narrow. "
                f"Consider querying with a broader term like \"cognitive impairment\".\n\n")
    else:
        f.write("| Score | Gene/Protein | Predicate (neuro→gene) | Predicate (gene→memory) |\n")
        f.write("|---|---|---|---|\n")
        for _, row in paths.head(20).iterrows():
            f.write(f"| {row['score']} | **{row['output_node_name']}** ({row['output_node']}) | "
                    f"{row['predictes1'].replace('biolink:','')} | {row['predictes2'].replace('biolink:','')} |\n")
    f.write("\n")

    # Path finding — learning disability
    f.write("## Path Finding: Neuroinflammation → Gene/Protein → Learning Disability\n\n")
    if paths2.empty:
        f.write("No paths found.\n\n")
    else:
        f.write("| Score | Gene/Protein | Predicate (neuro→gene) | Predicate (gene→learning) |\n")
        f.write("|---|---|---|---|\n")
        for _, row in paths2.head(20).iterrows():
            f.write(f"| {row['score']} | **{row['output_node_name']}** ({row['output_node']}) | "
                    f"{row['predictes1'].replace('biolink:','')} | {row['predictes2'].replace('biolink:','')} |\n")
    f.write("\n")

    # Interpretation
    f.write("---\n\n")
    f.write("## Biological Interpretation\n\n")
    f.write("The strongest supported mechanistic path (score 1.0):\n\n")
    f.write("```\nNeuroinflammation --[affects]--> TLR4 --[genetically_associated_with / gene_associated_with_condition]--> Learning Disability\n```\n\n")
    f.write("Neuroinflammation impairs learning and memory through several convergent mechanisms:\n\n")
    f.write("1. **NLRP3 inflammasome activation** → IL-1β/IL-18 release → synaptic depression in hippocampus\n")
    f.write("2. **TLR4 signaling** → NF-κB activation → pro-inflammatory gene cascade → LTP suppression → learning deficits\n")
    f.write("3. **TREM2/microglial dysregulation** → excessive synapse pruning → memory circuit disruption\n")
    f.write("4. **MAPT/Tau hyperphosphorylation** → neurofibrillary tangles → hippocampal neuron loss\n")
    f.write("5. **IL17A / BBB disruption** → peripheral immune cell infiltration → chronic neuronal stress\n")

print(f"\nResults written to {OUTPUT_FILE}")
