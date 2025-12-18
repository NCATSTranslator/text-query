from __future__ import annotations
from langchain_community.llms import CTransformers
from langchain_ollama import ChatOllama

COGITO_14B: ChatOllama = ChatOllama(
  model="cogito:14b",
  temperature=0.1,
  top_p=0.4,
  top_k=20,
  num_ctx=32_768,
  num_predict=2_048,
  repeat_penalty=1.1,
  repeat_last_n=64,      
)

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
