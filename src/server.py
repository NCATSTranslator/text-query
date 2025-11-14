from fastmcp import FastMCP

mcp = FastMCP("text-query")

@mcp.tool()
def example_tool(query: str) -> str:
    return f"Processed: {query}"

if __name__ == "__main__":
    mcp.run()
