from __future__ import annotations
from unnamed.llms import QuantizedMeditron7B
from langchain.agents import create_agent

Agent: QuantizedMeditron7B = create_agent(
  model=QuantizedMeditron7B
)

def main():
  print(Agent.invoke({"messages": [{"role": "user", "content": "How does the human gut microbiome affect ADHD?"}]}))