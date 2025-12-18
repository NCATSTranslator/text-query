from __future__ import annotations
from langchain_ollama import ChatOllama

QWEN_3_CODER_30B: ChatOllama = ChatOllama(
  model="qwen3-coder:30b",
  temperature=0.1,
  num_ctx=262_144,
  num_predict=2_048,
  top_k=40,
  top_p=0.9,
  repeat_penalty=1.15,
  repeat_last_n=64,
  num_batch=8,
)
