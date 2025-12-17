from __future__ import annotations
from langchain_mcp_adapters.client import MultiServerMCPClient 
from langchain.agents.structured_output import ToolStrategy
from unnamed.prompts import system_with_persona
from unnamed.llms import QUANTIZED_MEDITRON_7B
from langchain.messages import HumanMessage
from langchain.agents import create_agent
from unnamed.models import Response
from unnamed.models import Request
from unnamed.models import Context
from fastapi import FastAPI
import uvicorn

MCP_CLIENT: object = MultiServerMCPClient(
  {"MultiomicsKG Server": {"transport": "stdio", "command": "python3", "args": ["./mcps.py"]}}
)
MCP_TOOLS: object = MCP_CLIENT.get_tools()

AGENT: object = create_agent(
  model=QUANTIZED_MEDITRON_7B,
  tools=MCP_TOOLS,
  middleware=[system_with_persona],
  context_schema=Context,
  response_format=ToolStrategy(Response)
)

APP: FastAPI = FastAPI()

@APP.post("/", response_model=Response)
def invoke(x: Request):
  inputs: dict[str, list[HumanMessage]] = {"messages": [HumanMessage(x.content)]}
  result: object = AGENT.invoke(inputs, context=Context(persona=x.persona))
  return result["structured_response"]

def serve(host: str = "0.0.0.0", port: str = "8080") -> None:
  uvicorn.serve(APP, host=host, port=port)
