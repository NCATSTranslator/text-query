from fastmcp import FastMCP
from typing import Optional
import httpx
import json

MCP: object = FastMCP("MicrobiomeKG")

PLOVER_ENDPOINT: str = "https://multiomics.test.transltr.io/mbkp/query"
META_KG_ENDPOINT: str = "https://multiomics.test.transltr.io/mbkp/meta_knowledge_graph"

async def query_plover(query_graph: dict) -> dict:
  """Send TRAPI query to Plover endpoint and return response."""
  async with httpx.AsyncClient(timeout=60.0) as client:
    response = await client.post(
      PLOVER_ENDPOINT,
      json={"message": {"query_graph": query_graph}},
      headers={"Content-Type": "application/json"}
    )
    response.raise_for_status()
    return response.json()

@MCP.tool()
async def find_microbiome_for_disease(
  disease_id: str,
  disease_name: Optional[str] = None
) -> str:
  """
  Find microbial taxa (bacteria, organisms) associated with a specific disease.
  
  Args:
    disease_id: Disease identifier as CURIE (e.g., "MONDO:0013209" for NAFLD)
    disease_name: Optional human-readable disease name for context
  
  Returns:
    JSON string with microbial taxa associated with the disease, including
    relationship types, statistical significance (p-values), and source publications.
  
  Example:
    disease_id="MONDO:0013209" (NAFLD)
    disease_id="MONDO:0004664" (helminthiasis)
  """
  query_graph = {
    "nodes": {
      "disease": {"ids": [disease_id]},
      "microbe": {"categories": ["biolink:OrganismTaxon"]}
    },
    "edges": {
      "association": {
        "subject": "microbe",
        "predicates": ["biolink:associated_with", "biolink:correlated_with"],
        "object": "disease"
      }
    }
  }
  
  result = await query_plover(query_graph)
  
  summary = {
    "query": f"Microbiome taxa for {disease_name or disease_id}",
    "disease_id": disease_id,
    "result_count": len(result.get("message", {}).get("results", [])),
    "results": []
  }
  
  kg = result.get("message", {}).get("knowledge_graph", {})
  nodes = kg.get("nodes", {})
  edges = kg.get("edges", {})
  
  for res in result.get("message", {}).get("results", []):
    microbe_bindings = res.get("node_bindings", {}).get("microbe", [])
    
    for analysis in res.get("analyses", []):
      edge_bindings = analysis.get("edge_bindings", {}).get("association", [])
      
      for microbe_binding in microbe_bindings:
        microbe_id = microbe_binding.get("id")
        microbe_node = nodes.get(microbe_id, {})
        
        for edge_binding in edge_bindings:
          edge_id = edge_binding.get("id")
          edge = edges.get(edge_id, {})
          
          summary["results"].append({
            "microbe_id": microbe_id,
            "microbe_name": microbe_node.get("name"),
            "predicate": edge.get("predicate"),
            "p_value": edge.get("attributes", [{}])[0].get("value") if edge.get("attributes") else None,
            "publications": [attr.get("value") for attr in edge.get("attributes", []) if attr.get("attribute_type_id") == "biolink:publications"]
          })
  
  return json.dumps(summary, indent=2)

@MCP.tool()
async def find_diseases_for_microbe(
  microbe_id: str,
  microbe_name: Optional[str] = None
) -> str:
  """
  Find diseases or health conditions associated with a specific microbial taxon.
  
  Args:
    microbe_id: Microbe/organism identifier as CURIE (e.g., "NCBITaxon:815" for Bacteroides)
    microbe_name: Optional human-readable microbe name for context
  
  Returns:
    JSON string with diseases associated with the microbe, including
    relationship types, statistical significance (p-values), and source publications.
  
  Example:
    microbe_id="NCBITaxon:815" (Bacteroides genus)
  """
  query_graph = {
    "nodes": {
      "microbe": {"ids": [microbe_id]},
      "disease": {"categories": ["biolink:Disease", "biolink:PhenotypicFeature"]}
    },
    "edges": {
      "association": {
        "subject": "microbe",
        "predicates": ["biolink:associated_with", "biolink:correlated_with"],
        "object": "disease"
      }
    }
  }
  
  result = await query_plover(query_graph)
  
  summary = {
    "query": f"Diseases associated with {microbe_name or microbe_id}",
    "microbe_id": microbe_id,
    "result_count": len(result.get("message", {}).get("results", [])),
    "results": []
  }
  
  kg = result.get("message", {}).get("knowledge_graph", {})
  nodes = kg.get("nodes", {})
  edges = kg.get("edges", {})
  
  for res in result.get("message", {}).get("results", []):
    disease_bindings = res.get("node_bindings", {}).get("disease", [])
    
    for analysis in res.get("analyses", []):
      edge_bindings = analysis.get("edge_bindings", {}).get("association", [])
      
      for disease_binding in disease_bindings:
        disease_id = disease_binding.get("id")
        disease_node = nodes.get(disease_id, {})
        
        for edge_binding in edge_bindings:
          edge_id = edge_binding.get("id")
          edge = edges.get(edge_id, {})
          
          summary["results"].append({
            "disease_id": disease_id,
            "disease_name": disease_node.get("name"),
            "predicate": edge.get("predicate"),
            "p_value": edge.get("attributes", [{}])[0].get("value") if edge.get("attributes") else None,
            "publications": [attr.get("value") for attr in edge.get("attributes", []) if attr.get("attribute_type_id") == "biolink:publications"]
          })
  
  return json.dumps(summary, indent=2)

@MCP.tool()
async def explore_microbiome_disease_path(
  start_disease_id: str,
  end_disease_id: str,
  start_disease_name: Optional[str] = None,
  end_disease_name: Optional[str] = None
) -> str:
  """
  Explore potential connections between two diseases via shared microbiome associations.
  This finds microbes associated with both diseases to reveal potential mechanistic links.
  
  Args:
    start_disease_id: Starting disease CURIE (e.g., "MONDO:0004664")
    end_disease_id: Ending disease CURIE (e.g., "MONDO:0013209")
    start_disease_name: Optional human-readable name for start disease
    end_disease_name: Optional human-readable name for end disease
  
  Returns:
    JSON string describing microbes shared between both diseases, which may
    represent mechanistic connections.
  
  Example:
    start_disease_id="MONDO:0004664" (helminthiasis)
    end_disease_id="MONDO:0013209" (NAFLD)
  """
  query1 = {
    "nodes": {
      "disease": {"ids": [start_disease_id]},
      "microbe": {"categories": ["biolink:OrganismTaxon"]}
    },
    "edges": {
      "association": {
        "subject": "microbe",
        "predicates": ["biolink:associated_with", "biolink:correlated_with"],
        "object": "disease"
      }
    }
  }
  
  query2 = {
    "nodes": {
      "disease": {"ids": [end_disease_id]},
      "microbe": {"categories": ["biolink:OrganismTaxon"]}
    },
    "edges": {
      "association": {
        "subject": "microbe",
        "predicates": ["biolink:associated_with", "biolink:correlated_with"],
        "object": "disease"
      }
    }
  }
  
  result1 = await query_plover(query1)
  result2 = await query_plover(query2)
  
  microbes1 = set()
  _ = result1.get("message", {}).get("knowledge_graph", {})
  for res in result1.get("message", {}).get("results", []):
    for binding in res.get("node_bindings", {}).get("microbe", []):
      microbes1.add(binding.get("id"))
  
  microbes2 = set()
  kg2 = result2.get("message", {}).get("knowledge_graph", {})
  nodes2 = kg2.get("nodes", {})
  for res in result2.get("message", {}).get("results", []):
    for binding in res.get("node_bindings", {}).get("microbe", []):
      microbes2.add(binding.get("id"))
  
  shared_microbes = microbes1.intersection(microbes2)
  
  summary = {
    "query": f"Shared microbiome between {start_disease_name or start_disease_id} and {end_disease_name or end_disease_id}",
    "start_disease": {"id": start_disease_id, "name": start_disease_name},
    "end_disease": {"id": end_disease_id, "name": end_disease_name},
    "microbes_in_start": len(microbes1),
    "microbes_in_end": len(microbes2),
    "shared_microbes_count": len(shared_microbes),
    "shared_microbes": [
      {
        "id": microbe_id,
        "name": nodes2.get(microbe_id, {}).get("name", "Unknown")
      }
      for microbe_id in shared_microbes
    ]
  }
  
  return json.dumps(summary, indent=2)

@MCP.tool()
async def get_meta_knowledge_graph() -> str:
  """
  Retrieve the meta-knowledge graph describing what types of queries are possible.
  This shows all available node categories and edge predicates in the MicrobiomeKG.
  
  Returns:
    JSON string describing available query patterns, node types, and edge types.
  """
  async with httpx.AsyncClient(timeout=30.0) as client:
    response = await client.get(META_KG_ENDPOINT)
    response.raise_for_status()
    meta_kg = response.json()
  
  summary = {
    "description": "Available query patterns in MicrobiomeKG",
    "node_categories": set(),
    "predicates": set(),
    "edge_patterns": []
  }
  
  for edge in meta_kg.get("edges", []):
    summary["node_categories"].add(edge.get("subject"))
    summary["node_categories"].add(edge.get("object"))
    summary["predicates"].add(edge.get("predicate"))
    
    summary["edge_patterns"].append({
      "subject": edge.get("subject"),
      "predicate": edge.get("predicate"),
      "object": edge.get("object")
    })
  
  summary["node_categories"] = sorted(list(summary["node_categories"]))
  summary["predicates"] = sorted(list(summary["predicates"]))
  
  return json.dumps(summary, indent=2)

if __name__ == "__main__":
  MCP.run()
