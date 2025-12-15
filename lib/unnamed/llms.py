from __future__ import __annotations__
from langchain_community.llms import CTransformers

QuantizedMeditron7B: CTransformers = CTransformers(
  model="TheBloke/meditron-7B-GGUF",
  model_type="llama",
  model_file="meditron-7b.Q4_K_M.gguf",
  config={
    "max_new_tokens": 12,
    "temperature": 0.3,
    "top_k": 40,
    "top_p": 0.9,
    "repetition_penalty": 1.15,
    "last_n_tokens": 64,
    "threads": 4,
    "context_length": 2048,
    "batch_size": 8, 
  }
)