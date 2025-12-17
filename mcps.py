from __future__ import annotations
from neo4j import GraphDatabase
from typing import Optional
from fastmcp import FastMCP
from pathlib import Path
from typing import Any
import sqlite3

MCP: object = FastMCP(
  name="MultiomicsKG",
  instructions="""\
## Interface for MultiomicsKG. Retrieve validated biological connections.

### Procedure
1. **Identify**: Use `is_NODE` to find entities and retrieve `internal_id`. Use `is_MESH`/`MESH_means` for MESH terminology.
2. **Disambiguate**: Use returned labels/properties to select the correct entity.
3. **Connect**: Use `NODE_path` to find relationships.

### Constraints
* **Strict Dependency**: `NODE_path` inputs MUST be integer `internal_id`s obtained directly from `is_NODE`.
* **No Hallucination**: Never guess IDs or path inputs.
* **Scope**: `NODE_path` returns direct neighbors only.
"""
)

MESH: Path = Path("./.sqlite3/mesh.sqlite3")

@MCP.tool()
def MESH_means(x: Any) -> str:
  """What Does This MESH Code Mean?"""
  try:
    code: str = str(x)
    code = code.replace("MESH:", "") if "MESH:" in code else code

    with sqlite3.connect(MESH) as conn:
      try:
        cur: object = conn.cursor()
        cur.execute("SELECT term FROM mesh WHERE id = ?", (code))
        r: object = cur.fetchone()
        return r[0][0]
      finally:
        cur.close()

  finally:
    conn.close()

@MCP.tool()
def is_MESH(x: Any) -> str:
  """Is This A MESH Code?"""
  try:
    thing: str = str(x)

    with sqlite3.connect(MESH) as conn:
      try:
        cur: object = conn.cursor()
        cur.execute("SELECT id FROM mesh WHERE term = ?", (thing))
        r: object = cur.fetchone()
        return r[0][0]
      finally:
        cur.close()

  finally:
    conn.close()

# ! Hosting Info Is In The ./.neo4j/conf/neo4j.conf -- Change If The Driver Breaks
DRIVER: object = GraphDatabase.driver("bolt://localhost:7687", auth=None)

def is_NODE(x: Any, exact_match: bool = False, labels: Optional[list[str]] = None, limit: int = 3) -> list[dict[str, str]]:
  """Does This Exist As A Node In MultiomicsKG? Returns Found Nodes As A List."""
  try:
    thing: str = str(x)

    with DRIVER.session() as session:
      label_clause: str = "" if not labels else ":" + ":".join(labels)

      if exact_match:
        where_clause: str = """\
toLower(n.name) = toLower($thing) OR 
toLower(n.title) = toLower($thing) OR 
toLower(n.label) = toLower($thing) OR 
toLower(n.id) = toLower($thing)
"""
      else:
        where_clause = """\
toLower(n.name) CONTAINS toLower($thing) OR 
toLower(n.title) CONTAINS toLower($thing) OR 
toLower(n.label) CONTAINS toLower($thing) OR 
toLower(n.id) CONTAINS toLower($thing)
"""

      query: str = f"""\
MATCH (n{label_clause})
WHERE {where_clause}
RETURN n, labels(n) as node_labels, id(n) as internal_id
LIMIT $limit
"""

      r: object = session.run(query, thing=thing, limit=limit)
      records: object = r.data()

      if not r.records:
        return []
      else:
        return [
          {
            "internal_id": t["internal_id"],
            "labels": t["node_labels"],
            "properties": dict(t["n"])
          }
          for t in records
        ]

  finally:
    DRIVER.close()

def NODE_path(source_id: Any, target_id: Any, limit: int = 3) -> list[dict[str, Any]]:
  """Finds Paths Between Two Nodes. Returns Found Paths As A List."""
  try:
    id1 = str(source_id)
    id2 = str(target_id)

    with DRIVER.session() as session:
      query: str = """
MATCH (node1), (node2)
WHERE id(node1) = $id1 AND id(node2) = $id2
MATCH path = (node1)-(node2)
RETURN path
LIMIT $limit
"""

      r: object = session.run(query, id1=id1, id2=id2, limit=limit)
      records: object = r.data()

      if not r.records:
        return []
      else:

        paths: list[dict[str, Any]] = []
        for t in records:
          p: object = t["path"]
          nodes: object = p.nodes
          relationships: object = p.relationships

          info: dict[str, Any] = {
            "length": len(relationships),
            "nodes": {
              {
                "labels": list(y.labels),
                "properties": dict(y)
              }
              for y in nodes
            },
            "relationships": {
              {
                "type": z.type,
                "properties": dict(z)
              }
              for z in relationships
            }
          }

          paths.append(info)

        return paths

  finally:
    DRIVER.close()

if __name__ == "__main__":
  MCP.run()
