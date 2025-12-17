from __future__ import annotations
from langchain.agents.middleware import SummarizationMiddleware
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents.structured_output import ToolStrategy
from langgraph.checkpoint.memory import InMemorySaver
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

SUMMARIZER: object = SummarizationMiddleware(
  model=QUANTIZED_MEDITRON_7B,
  trigger=("tokens", 1600),
  keep=("messages", 20)
)

AGENT: object = create_agent(
  model=QUANTIZED_MEDITRON_7B,
  tools=MCP_TOOLS,
  middleware=[
    system_with_persona,
    SUMMARIZER
  ],
  context_schema=Context,
  response_format=ToolStrategy(Response),
  checkpointer=InMemorySaver
)

APP: FastAPI = FastAPI()

@APP.post("/", response_model=Response)
def invoke(x: Request):
  inputs: dict[str, list[HumanMessage]] = {"messages": [HumanMessage(x.content)]}
  result: object = AGENT.invoke(inputs, {"configurable": {"thread_id": "1"}}, context=Context(persona=x.persona))
  return result["structured_response"]

def serve(host: str = "0.0.0.0", port: str = "8080") -> None:
  uvicorn.serve(APP, host=host, port=port)
