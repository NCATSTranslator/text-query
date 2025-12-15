from __future__ import __annotations__
from unnamed.llms import QuantizedMeditron7B
from langchain.agents import create_agent

Agent: QuantizedMeditron7B = create_agent(
  model=QuantizedMeditron7B
)

def main():
  print(Agent.invoke({"messages": [{"content": "What is the microbiome?"}]}))