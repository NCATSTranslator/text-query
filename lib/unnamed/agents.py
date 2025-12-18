from __future__ import annotations
from langchain.agents.middleware import SummarizationMiddleware
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents.structured_output import ToolStrategy
from langgraph.checkpoint.memory import InMemorySaver
from unnamed.llms import HERMES_2_PRO_LLAMA_3_8B
from unnamed.prompts import system_with_persona
from langchain.messages import HumanMessage
from langchain.agents import create_agent
from unnamed.models import Response
from unnamed.models import Request
from unnamed.models import Context
from fastapi import FastAPI
from os import environ
import asyncio
import uvicorn

MCP_CLIENT: object = MultiServerMCPClient(
  {"MultiomicsKG Server": {"transport": "stdio", "command": environ.get("PYTHON_INTERPRETER"), "args": ["./mcps.py"]}}
)
MCP_TOOLS: object = asyncio.run(MCP_CLIENT.get_tools())

SUMMARIZER: object = SummarizationMiddleware(
  model=HERMES_2_PRO_LLAMA_3_8B,
  max_tokens_before_summary=1_600,
  messages_to_keep=5
)

AGENT: object = create_agent(
  model=HERMES_2_PRO_LLAMA_3_8B,
  tools=MCP_TOOLS,
  middleware=[
    system_with_persona,
    SUMMARIZER
  ],
  context_schema=Context,
  response_format=ToolStrategy(Response),
  checkpointer=InMemorySaver()
)

APP: FastAPI = FastAPI()

@APP.post("/", response_model=Response)
def invoke(x: Request):
  inputs: dict[str, list[HumanMessage]] = {"messages": [HumanMessage(x.content)]}
  result: object = AGENT.invoke(inputs, {"configurable": {"thread_id": "1"}}, context=Context(persona=x.persona))
  return result["structured_response"]

def serve(host: str = "127.0.0.1", port: str = "8080") -> None:
  uvicorn.run(APP, host=host, port=port)
