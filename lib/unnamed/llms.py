from __future__ import annotations
from langchain_ollama import ChatOllama

COGITO_8B: ChatOllama = ChatOllama(
  model="cogito:8b",
  temperature=0.1,
  top_p=0.4,
  top_k=20,
  num_ctx=32_768,
  num_predict=2_048,
  repeat_penalty=1.1,
  repeat_last_n=64,      
)

