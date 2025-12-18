from __future__ import annotations
from langchain.agents.middleware import ModelCallLimitMiddleware
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents.structured_output import ToolStrategy
from langchain.agents.middleware import TodoListMiddleware
from langgraph.checkpoint.memory import InMemorySaver
from unnamed.prompts import system_with_persona
from langchain.messages import HumanMessage
from langchain.agents import create_agent
from unnamed.models import Response
from unnamed.llms import COGITO_8B
from unnamed.models import Request
from unnamed.models import Context
from fastapi import FastAPI
from os import environ
import asyncio
import uvicorn

PYTHON: str = environ.get("PYTHON_INTERPRETER")

MCP_CLIENT: object = MultiServerMCPClient({
  "MultiomicsKG": {"transport": "stdio", "command": PYTHON, "args": ["./.mcps/mokg.py"]},
  "MeSH": {"transport": "stdio", "command": PYTHON, "args": ["./.mcps/mesh.py"]},
  # "MicrobiomeKG": {"transport": "stdio", "command": PYTHON, "args": ["./.mcps/mbkg.py"]}
})

async def get_mcps() -> object:
  return await MCP_CLIENT.get_tools()

APP: FastAPI = FastAPI()

@APP.on_event("startup")
async def startup() -> None:
  await get_mcps()

@APP.post("/", response_model=Response)
async def invoke(x: Request) -> Response:
  tools: object = await get_mcps()

  call_limit: object = ModelCallLimitMiddleware(
    run_limit=10,
    exit_behavior="end"
  )

  todo_list: object = TodoListMiddleware()

  agent: object = create_agent(
    model=COGITO_8B,
    tools=tools,
    middleware=[
      system_with_persona,
      call_limit,
      todo_list
    ],
    context_schema=Context,
    response_format=ToolStrategy(Response),
    checkpointer=InMemorySaver(),
    debug=True
  )

  inputs: dict[str, list[HumanMessage]] = {"messages": [HumanMessage(x.content)]}
  r: object = await agent.ainvoke(
    inputs,
    {"configurable": {"thread_id": "1"}},
    context=Context(persona=x.persona)
  )

  print(r)
  content: object = r["messages"][-1]
  return Response(content=content.content)

def serve(host: str = "127.0.0.1", port: str = "8080") -> None:
  uvicorn.run(APP, host=host, port=port)
