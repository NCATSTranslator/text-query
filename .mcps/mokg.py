from __future__ import annotations
from neo4j import GraphDatabase
from typing import Optional
from fastmcp import FastMCP
from typing import Any
import json

MCP: object = FastMCP(
  name="MultiomicsKG",
  instructions="""\
Interface for MultiomicsKG. This is the ONLY way to query the MultiomicsKG knowledge graph. All queries must go through these tools.

Node Identity:
- Nodes use CURIE identifiers (e.g., HGNC:1234, MONDO:0005148)
- Node categories follow Biolink Model ontology (e.g., biolink:Gene, biolink:Disease)
- Use is_NODE to search for entities and retrieve their internal_id (integer)

Relationships:
- Predicates follow Biolink Model ontology (e.g., biolink:treats, biolink:associated_with)
- Edges are annotated with MeSH terms for semantic context
- MeSH terms are references only - use the MeSH MCP to interpret their meaning
- You CANNOT query by MeSH term in this MCP

Workflow:
1. Search: Use is_NODE to find entities by name/label/id. Specify exact_match=True for precise lookups or False for fuzzy search.
2. Disambiguate: Use returned labels and properties to select the correct entity.
3. Connect: Use NODE_path with internal_id integers from is_NODE to find direct relationships between nodes.

Constraints:
- NODE_path requires integer internal_id values obtained from is_NODE - never guess or fabricate IDs
- NODE_path returns direct neighbors only (single-hop paths)
- All node identifiers use standard biomedical CURIEs
- All predicates and categories use Biolink Model vocabulary

Example Data:
- Use example_edge resource to see the full structure of edge properties including provenance, statistical measures, and publication metadata
- Use example_node resource to see the structure of node properties with CURIE identifiers and Biolink categories
"""
)

@MCP.resource("resource://example-edge")
def example_edge() -> str:
  """
  Example edge structure from MultiomicsKG showing all available properties.

  Returns:
    JSON string containing a representative edge with:
    - subject/object: CURIE identifiers for connected nodes
    - predicate: Biolink Model relationship type
    - statistical_evidence: significance, p_value, score, relationship_strength
    - methodology: assertion_method, multiple_testing_correction_method, sample_size
    - provenance: publication details (PMC ID, authors, journal, year, title)
    - mesh_terms: MeSH code annotations (interpret using MeSH MCP)
    - mapping_metadata: subject/object names, categories, taxon, database sources
    - data_source: download_link, file details, curator information

  Note:
    This shows the rich metadata available on edges including statistical validation,
    scientific provenance, and semantic annotations. Use this as reference for
    understanding what information is available when querying relationships.
  """
  edge: str = """\
{"subject":"UniProtKB:Q9C002","predicate":"biolink:correlated_with","object":"MONDO:0005044","significant":"YES","score":100.0,"domain":"NA","mesh_terms":"MESH:D000349","sample_size":"about 40,000","p_value":"0.035945","multiple_testing_correction_method":"Bonferroni adjustment","relationship_strength":"0.024152","assertion_method":"regression","notes":"Large-scale plasma proteomics comparisons through genetics and disease associations","knowledge_level":"statistical_association","agent_type":"data_analysis_pipeline","publication":"PMC:PMC10567571","first_author":"Eldjarn","journal":"Nature","article_title":"Large-scale plasma proteomics comparisons through genetics and disease associations.","year_published":"2023","download_link":"https://static-content.springer.com/esm/art%3A10.1038%2Fs41586-023-06563-x/MediaObjects/41586_2023_6563_MOESM3_ESM.xlsx","file_name":"41586_2023_6563_MOESM3_ESM.xlsx","section_number":2,"file_extension":"xlsx","sheet_name":"ST17_somascan_phenotype_assoc","source_row_number":196731,"supplementary_file_caption":"Supplementary Tables 1&#x02013;2, 6, 12, 14&#x02013;33 and 35&#x02013;40.","original_subject":"NMES1","subject_name":"NMES1_HUMAN Normal mucosa of esophagus-specific gene 1 protein (sprot)","subject_category":"biolink:Protein","subject_mapped_with_taxon":"NCBITaxon:9606","subject_mapped_with_database":"babel","subject_mapped_with_level":"L1","original_object":"Hypertension","object_name":"hypertension","object_category":"biolink:Disease","object_mapped_with_taxon":"NA","object_mapped_with_database":"babel","object_mapped_with_level":"L1","config_curator_name":"JC Roach; Nov 3, 2025 AND SL Goetz; Dec 12, 2025","config_curator_organization":"Institute for Systems Biology"}
"""
  return json.dumps(edge, indent=2)

@MCP.resource("resource://example-node")
def example_node() -> str:
  """
  Example node structure from MultiomicsKG showing standard properties.

  Returns:
    JSON string containing a representative node with:
    - id: CURIE identifier (e.g., NCBIGene:125228)
    - name: Human-readable entity name
    - category: Biolink Model category (e.g., biolink:Gene, biolink:Disease)
    - taxon: CURIE for species/organism (e.g., NCBITaxon:9606 for human)

  Note:
    This shows the minimal core properties all nodes possess. Additional properties
    may exist depending on the node type and data source. Use this as reference for
    understanding node structure when parsing is_NODE results.
  """
  node: str = """\
{"id":"NCBIGene:125228","name":"FAM210A","category":"biolink:Gene","taxon":"NCBITaxon:9606"}
"""
  return json.dumps(node, indent=2)

# ! Hosting Info Is In The ./.neo4j/conf/neo4j.conf -- Change If The Driver Breaks
DRIVER: object = GraphDatabase.driver("bolt://localhost:7687", auth=None)

@MCP.tool()
def is_NODE(x: Any, exact_match: bool = False, labels: Optional[list[str]] = None, limit: int = 3) -> str:
  """
  Search for nodes in MultiomicsKG by name, label, title, or CURIE identifier.

  Args:
    x: Search term (str) - can be entity name, label, or CURIE
    exact_match: If True, requires exact string match; if False, performs fuzzy CONTAINS search
    labels: Optional list of Biolink Model category filters (e.g., ["biolink:Gene", "biolink:Disease"])
    limit: Maximum number of results to return (default 3)

  Returns:
    JSON string containing list of matching nodes with internal_id, Biolink categories, and properties including CURIE identifiers
  """
  print("CALLED | 1")
  try:
    thing: str = str(x)

    with DRIVER.session() as session:
      if labels:
        escaped_labels = [f"`{label}`" if ":" in label else label for label in labels]
        label_clause: str = ":" + ":".join(escaped_labels)
      else:
        label_clause: str = ""

      if exact_match:
        where_clause: str = """\
toLower(n.name) = toLower($thing) OR 
toLower(n.id) = toLower($thing)
"""
      else:
        where_clause = """\
toLower(n.name) CONTAINS toLower($thing) OR 
toLower(n.id) CONTAINS toLower($thing)
"""

      query: str = f"""\
MATCH (n{label_clause})
WHERE {where_clause}
RETURN n, labels(n) as node_labels, elementId(n) as internal_id
LIMIT $limit
"""

      r: object = session.run(query, thing=thing, limit=limit)
      records: list = r.data()

      if not records:
        return json.dumps([], indent=2)
      else:
        nodes: list[dict[str, Any]] = [
          {
            "internal_id": t["internal_id"],
            "labels": t["node_labels"],
            "properties": dict(t["n"])
          }
          for t in records
        ]
        return json.dumps(nodes, indent=2)

  finally:
    DRIVER.close()

@MCP.tool()
def NODE_path(source_id: Any, target_id: Any, limit: int = 3) -> str:
  """
  Find direct relationships (single-hop paths) between two nodes in MultiomicsKG.

  Args:
    source_id: Internal node ID (string) obtained from is_NODE - must be exact internal_id value (elementId)
    target_id: Internal node ID (string) obtained from is_NODE - must be exact internal_id value (elementId)
    limit: Maximum number of paths to return (default 3)

  Returns:
    JSON string containing paths with:
    - Node information: Biolink categories, properties with CURIEs
    - Relationship information: Biolink predicates, properties including MeSH term annotations

  Note:
    - Only returns direct neighbor connections (length 1 paths)
    - Relationship properties may include MeSH terms - use MeSH MCP to interpret their meaning
    - Never fabricate or guess internal_id values
    - internal_id is now a string (elementId) not an integer
  """
  try:
    id1 = str(source_id)
    id2 = str(target_id)

    with DRIVER.session() as session:
      query: str = """
MATCH (node1), (node2)
WHERE elementId(node1) = $id1 AND elementId(node2) = $id2
MATCH path = (node1)--(node2)
RETURN path
LIMIT $limit
"""

      r: object = session.run(query, id1=id1, id2=id2, limit=limit)
      records: list = r.data()

      if not records:
        return json.dumps([], indent=2)
      else:

        paths: list[dict[str, Any]] = []
        for t in records:
          p: object = t["path"]
          nodes: object = p.nodes
          relationships: object = p.relationships

          info: dict[str, Any] = {
            "length": len(relationships),
            "nodes": [
              {
                "labels": list(y.labels),
                "properties": dict(y)
              }
              for y in nodes
            ],
            "relationships": [
              {
                "type": z.type,
                "properties": dict(z)
              }
              for z in relationships
            ]
          }

          paths.append(info)

        return json.dumps(paths, indent=2)

  finally:
    DRIVER.close()

if __name__ == "__main__":
  MCP.run()
