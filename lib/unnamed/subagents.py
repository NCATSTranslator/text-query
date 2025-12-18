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

# ! Do Not Change This To "tool" Or "tools" Because MCPs Call Those Variables Internally
@tool()
async def ask_medical_subagent(x: str) -> str:
  """
  Query a specialized medical AI assistant for terminology, concepts, and biomedical knowledge.

  Args:
    x: Natural language question about medical/biological topics

  Returns:
    JSON string containing the medical assistant's response

  Use Cases:
    - Expand medical abbreviations (e.g., "What is the full name for ADHD?")
    - Find alternative names for medical terms (e.g., "What are synonyms for hypertension?")
    - Clarify proper database terminology formatting (e.g., "How is ADHD written in MONDO?")
    - Explain biological entities (e.g., "What is Bifidobacterium?")
    - Disambiguate medical concepts when searches fail

  Workflow:
    1. When is_NODE returns empty results, use this tool to expand abbreviations or find alternative names
    2. Ask for database-specific formatting (MONDO, UMLS, NCBITaxon conventions)
    3. Request multiple name variations to try in subsequent searches

  Examples:
    - "What is the full medical name for ADHD?"
    - "What are alternative names for attention deficit hyperactivity disorder?"
    - "How is type 2 diabetes formally written in medical databases?"
    - "What does COPD stand for?"
    - "Explain what Bifidobacterium is"

  Note:
    Always consult this tool before concluding a medical entity doesn't exist in the knowledge graph.
    The assistant provides accurate terminology aligned with biomedical ontologies.
  """
  inputs: dict[str, list[HumanMessage]] = {"messages": [HumanMessage(x)]}
  r: object = MEDICAL_SUBAGENT.invoke(inputs)
  context: object = r["messages"][-1].content
  return json.dumps(context, indent=2)