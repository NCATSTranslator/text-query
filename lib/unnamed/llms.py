from __future__ import annotations
from langchain_community.llms import CTransformers
from langchain_ollama import ChatOllama

QWEN_CODER_2_5_7B: ChatOllama = ChatOllama(
  model="qwen2.5-coder:7b",
  temperature=0.3,
  num_ctx=2048,
  num_predict=512,
  top_k=40,
  top_p=0.9,
  repeat_penalty=1.15,
  repeat_last_n=64,
  num_batch=8,
)

QUANTIZED_MEDITRON_7B: CTransformers = CTransformers(
  model="TheBloke/meditron-7B-GGUF",
  model_type="llama",
  model_file="meditron-7b.Q4_K_M.gguf",
  config={
    "max_new_tokens": 512,
    "temperature": 0.3,
    "top_k": 40,
    "top_p": 0.9,
    "repetition_penalty": 1.15,
    "last_n_tokens": 64,
    "context_length": 2048,
    "batch_size": 8, 
  }
)
