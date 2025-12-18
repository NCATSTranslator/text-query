from __future__ import annotations
from fastmcp import FastMCP
from pathlib import Path
from typing import Any
import sqlite3
import json

MCP: object = FastMCP(
  name="MeSH",
  instructions="""\
Interface for MeSH (Medical Subject Headings) terminology database. Use this to interpret MeSH terms that annotate edges in MultiomicsKG.

MeSH Context:
- MeSH terms are metadata annotations on relationships (edges) in MultiomicsKG
- MeSH terms are NOT nodes themselves - they describe semantic context of connections
- MeSH descriptors provide controlled vocabulary for biomedical concepts
- Each MeSH code (e.g., D000001) maps to standardized medical terminology

Workflow:
1. Interpret: Use MESH_means to look up what a MeSH code from a MultiomicsKG edge means
2. Search: Use is_MESH to find the MeSH code for a specific medical term

Constraints:
- MeSH terms annotate edges only - they are not queryable as nodes in MultiomicsKG
- Use this MCP to understand edge annotations, not to search for graph entities
- MeSH codes follow format like D000001, C000001, etc. (optionally prefixed with "MESH:")
"""
)

MESH: Path = Path("./.sqlite3/mesh.sqlite3")

@MCP.tool()
def MESH_means(x: Any) -> str:
  """
  Look up the meaning and definition of a MeSH code.

  Args:
    x: MeSH code (str) - can be formatted as "D000001" or "MESH:D000001"

  Returns:
    JSON string containing MeSH descriptor information including term name, definition, and metadata

  Note:
    Use this to interpret MeSH codes found in MultiomicsKG edge annotations
  """
  try:
    code: str = str(x)
    code = code.replace("MESH:", "") if "MESH:" in code else code

    with sqlite3.connect(MESH) as conn:
      try:
        cur: object = conn.cursor()
        cur.execute("SELECT * FROM mesh WHERE id = ?", (code,))
        r: object = cur.fetchone()
        return json.dumps(r, indent=2)

      finally:
        cur.close()

  finally:
    conn.close()

@MCP.tool()
def is_MESH(x: Any) -> str:
  """
  Search for a MeSH code by medical term or concept name.

  Args:
    x: Medical term or concept name (str) - exact match required

  Returns:
    JSON string containing matching MeSH descriptor with code, term, and metadata

  Note:
    Use this to find the MeSH code for a specific medical concept when you know the term name
  """
  try:
    thing: str = str(x)

    with sqlite3.connect(MESH) as conn:
      try:
        cur: object = conn.cursor()
        cur.execute("SELECT * FROM mesh WHERE term = ?", (thing,))
        r: object = cur.fetchone()
        return json.dumps(r, indent=2)

      finally:
        cur.close()

  finally:
    conn.close()

if __name__ == "__main__":
  MCP.run()
