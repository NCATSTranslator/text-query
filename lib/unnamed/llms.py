from __future__ import annotations
from langchain_community.llms import CTransformers
from langchain_ollama import ChatOllama

QWEN_3_CODER_30B: ChatOllama = ChatOllama(
  model="qwen3-coder:30b",
  temperature=0.3,
  num_ctx=262_144,
  num_predict=2_048,
  top_k=40,
  top_p=0.9,
  repeat_penalty=1.15,
  repeat_last_n=64,
  num_batch=8,
  format="json",
)

"""
QUANTIZED_MEDITRON_7B: CTransformers = CTransformers(
  model="TheBloke/meditron-7B-GGUF",
  model_type="llama",
  model_file="meditron-7b.Q4_K_M.gguf",
  config={
    "max_new_tokens": 1024,
    "temperature": 0.3,
    "top_k": 40,
    "top_p": 0.9,
    "repetition_penalty": 1.15,
    "last_n_tokens": 64,
    "context_length": 2048,
    "batch_size": 8, 
  }
)
"""