from __future__ import annotations
from langchain_community.llms import CTransformers
from langchain_openai import ChatOpenAI

HERMES_2_PRO_LLAMA_3_8B: ChatOpenAI = ChatOpenAI(
  model="NousResearch/Hermes-2-Pro-Llama-3-8B",
  openai_api_key="EMPTY",
  openai_api_base="http://localhost:8000/v1",
  max_tokens=5,
  temperature=0.3,
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
