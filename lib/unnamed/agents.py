from __future__ import annotations
from langchain.agents.middleware import SummarizationMiddleware
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents.structured_output import ToolStrategy
from langgraph.checkpoint.memory import InMemorySaver
from unnamed.prompts import system_with_persona
# from unnamed.llms import QUANTIZED_MEDITRON_7B
from langchain.messages import HumanMessage
from unnamed.llms import QWEN_3_CODER_30B
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
  model=QWEN_3_CODER_30B,
  max_tokens_before_summary=1_600,
  messages_to_keep=5
)

AGENT: object = create_agent(
  model=QWEN_3_CODER_30B,
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
  r: object = AGENT.invoke(inputs, {"configurable": {"thread_id": "1"}}, context=Context(persona=x.persona))
  print(r)
  content: object = r["messages"][-1]
  return Response(content=content.content)

def serve(host: str = "127.0.0.1", port: str = "8080") -> None:
  uvicorn.run(APP, host=host, port=port)
