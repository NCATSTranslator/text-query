from __future__ import annotations
from neo4j import GraphDatabase
from typing import Optional
from fastmcp import FastMCP
from pathlib import Path
from typing import Any
import sqlite3

MCP: object = FastMCP(
  name="MultiomicsKG Server"
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

def is_NODE(x: str, exact_match: bool = False, labels: Optional[list[str]] = None) -> list[dict[str, str]]:
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
LIMIT 3
"""

      r: object = session.run(query, thing=thing)
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

if __name__ == "__main__":
  MCP.run()
