from __future__ import annotations
from unnamed.llms import QUANTIZED_MEDITRON_7B
from langchain.messages import HumanMessage
from langchain.agents import create_agent
from langchain.tools import tool
import json

MEDICAL_SUBAGENT: object = create_agent(
  model=QUANTIZED_MEDITRON_7B,
  debug=True
)

@tool()
async def ask_medical_subagent(x: str) -> str:
  """
  Query a specialized medical AI assistant for terminology, knowledge graph interpretation, and biomedical knowledge.

  Args:
    x: Natural language question about medical/biological topics or knowledge graph results

  Returns:
    JSON string containing the medical assistant's response

  Use Cases:
    - Expand medical abbreviations (e.g., "What is the full name for ADHD?")
    - Find alternative names for medical terms (e.g., "What are synonyms for hypertension?")
    - Clarify proper database terminology formatting (e.g., "How is ADHD written in MONDO?")
    - Explain biological entities (e.g., "What is Bifidobacterium?")
    - Disambiguate medical concepts when searches fail
    - Interpret knowledge graph results (e.g., "Explain these disease-gene associations")
    - Summarize complex biomedical relationships (e.g., "What do these pathways tell us about this condition?")
    - Contextualize graph query outputs (e.g., "What's the clinical significance of these findings?")

  Workflow:
    1. When is_NODE returns empty results, use this tool to expand abbreviations or find alternative names
    2. Ask for database-specific formatting (MONDO, UMLS, NCBITaxon conventions)
    3. Request multiple name variations to try in subsequent searches
    4. After obtaining knowledge graph results, use this tool to interpret, summarize, and explain findings
    5. Request clinical context or mechanistic explanations for graph relationships

  Examples:
    Terminology:
    - "What is the full medical name for ADHD?"
    - "What are alternative names for attention deficit hyperactivity disorder?"
    - "How is type 2 diabetes formally written in medical databases?"
    
    Interpretation:
    - "Explain what these gene-disease associations mean: [results]"
    - "Summarize the clinical relevance of these protein interactions: [results]"
    - "What do these microbiome-disease relationships suggest about pathogenesis?"
    - "Interpret these pathway enrichment results in the context of inflammation"

  Note:
    This tool serves dual purposes: (1) finding entities before querying, and (2) making sense of 
    query results afterward. Always consult for terminology before concluding an entity doesn't exist,
    and use it to interpret complex knowledge graph outputs for clinical or biological insights.
  """
  inputs: dict[str, list[HumanMessage]] = {"messages": [HumanMessage(x)]}
  r: object = await MEDICAL_SUBAGENT.ainvoke(inputs)
  context: object = r["messages"][-1].content
  return json.dumps(context, indent=2)
