from __future__ import annotations
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
    with sqlite3.connect(sqlite3) as conn:
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
    with sqlite3.connect(sqlite3) as conn:
      try:
        cur: object = conn.cursor()
        cur.execute("SELECT id FROM mesh WHERE term = ?", (thing))
        r: object = cur.fetchone()
        return r[0][0]
      finally:
        cur.close()
  finally:
    conn.close()
