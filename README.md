# text-query

A FastMCP server.

## Setup

Install dependencies using uv:

```bash
uv sync
```

## Development

Run the server in development mode:

```bash
uv run src/server.py
```

## Usage

Add to your Claude Desktop configuration file at `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "microbiome-query": {
      "command": "/Users/YOUR_USERNAME/.local/bin/uv",
      "args": [
        "--directory",
        "/path/to/text-query",
        "run",
        "src/server.py"
      ]
    }
  }
}
```

Replace:
- `YOUR_USERNAME` with your actual username
- `/path/to/text-query` with the full path to this repository

Find the full path to `uv` with:
```bash
which uv
```

After updating the config, restart Claude Desktop.
