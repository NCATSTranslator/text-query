# ? Makes The Neo4j Database For The MOKG MCP
from __future__ import annotations
from neo4j import GraphDatabase
from pathlib import Path
import orjson
import typer

APP: object = typer.Typer(pretty_exceptions_show_locals=False)

# ! Hosting Info Is In The ./.neo4j/conf/neo4j.conf -- Change If The Driver Breaks
DRIVER: object = GraphDatabase.driver("bolt://localhost:7687", auth=None)

def import_nodes(session: object, nodes: Path, max_batch: int = 2_000) -> None:
  node_insert: str = r"""\
UNWIND $batch AS node
MERGE (n:Node {id: node.id})
SET n.name = node.name,
    n.category = node.category,
    n.taxon = node.taxon
"""
  with nodes.open("rb") as f:
    batch: list[object] = []
    for idx, line in enumerate(f, start=1):
      node = orjson.loads(line)
      batch.append(node)

      if len(batch) >= max_batch:
        session.run(node_insert, batch=batch)
        batch = []
        print(f"Inserted {idx} Nodes")

    if batch:
      session.run(node_insert, batch=batch)

    print(f"Finished Inserting Nodes")

def import_edges(session: object, edges: Path, max_batch: int = 1_000) -> None:
  edge_insert: str = r"""\
UNWIND $batch AS edge
MATCH (s:Node {id: edge.subject})
MATCH (o:Node {id: edge.object})
MERGE (s)-[r:RELATED_TO {predicate: edge.predicate}]->(o)
SET r += edge
"""
  with edges.open("rb") as f:
    batch: list[object] = []
    for idx, line in enumerate(f, start=1):
      edge = orjson.loads(line)
      batch.append(edge)

      if len(batch) >= max_batch:
        session.run(edge_insert, batch=batch)
        batch = []
        print(f"Inserted {idx} Edges")

    if batch:
      session.run(edge_insert, batch=batch)

    print(f"Finished Inserting Edges")

@APP.command()
def main(
  nodes: Path = typer.Option(..., "-n", "-nodes", help="Path To The MOKG-Nodes NDJSON Export"),
  edges: Path = typer.Option(..., "-e", "-edges", help="Path To The MOKG-Edges NDJSON Export")
) -> None:
  """Makes The Neo4j Database For The MOKG MCP"""
  try:
    with DRIVER.session() as session:
      session.run("CREATE INDEX curies IF NOT EXISTS FOR (n:Node) ON (n.id)")
      import_nodes(session, nodes)
      import_edges(session, edges)
  finally:
    DRIVER.close()
    print("Inserts Complete")

if __name__ == "__main__":
  APP()
