# docsearch-mcp

A small [MCP](https://modelcontextprotocol.io) server that lets an AI assistant search a folder of Markdown docs. It's built with [FastMCP](https://gofastmcp.com) and exposes one tool, `doc_search`. The sample corpus is four pages from the [Prefect docs](https://docs.prefect.io): flows, tasks, caching, and assets.

> Ask *"how does cache expiration work?"* and the assistant calls `doc_search`, gets back the most relevant sections, and answers from them.

## How it works

```
query ──► drop stop words ──► split each .md on "## " headings
      ──► score each section ──► sort ──► top N as {file, heading, snippet, score}
```

- **Whole-word matching.** Text is tokenized with `\w+`, so `i` doesn't match inside `file`.
- **Stop-word filter.** Filler words like `how`, `do`, `a`, and `the` don't score.
- **Heading boost.** A query word in the section heading adds +2, so "Cache expiration" beats a passing mention.
- **Folder-relative paths.** `docs/` is found from `__file__`, so the server works however a client launches it.

Example: `doc_search("cache key expiration", limit=2)`

```json
[
  { "file": "prefect_caching.md", "heading": "Customizing the cache", "score": 45, "snippet": "Prefect allows you to configure task caching behavior..." },
  { "file": "prefect_caching.md", "heading": "Cache policies",        "score": 22, "snippet": "Cache key computation can be configured through..." }
]
```

## Quickstart

Requires Python 3.10+. [uv](https://docs.astral.sh/uv/) is recommended.

```bash
git clone https://github.com/sanster9292/docsearch-mcp.git
cd docsearch-mcp
uv venv --python 3.12 && source .venv/bin/activate
uv pip install fastmcp
```

### Run over HTTP

```bash
fastmcp run fast_server.py:mcp --transport http --port 8000
```

The endpoint is `http://localhost:8000/mcp`. Opening it in a browser returns `Missing session ID`, which is expected: MCP clients must send `initialize` first to get an `mcp-session-id`.

### Test it

**Python client.** Run this with the server running:

```bash
python test_client.py
```

**MCP Inspector (UI):**

```bash
npx @modelcontextprotocol/inspector
```

Add a server with the Streamable HTTP transport and the URL `http://localhost:8000/mcp`, then go to Tools → `doc_search`.

### Use it from Claude Desktop (stdio)

Add this to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "docsearch": {
      "command": "/absolute/path/to/docsearch-mcp/.venv/bin/fastmcp",
      "args": ["run", "/absolute/path/to/docsearch-mcp/fast_server.py:mcp"]
    }
  }
}
```

## Use your own docs

Drop any `.md` files into `docs/`. Sections are split on `## ` headings, and text above the first heading is indexed as "Introduction". No restart is needed for new files, because the folder is read on every call.

## Project layout

```
docsearch-mcp/
├── fast_server.py   # FastMCP server + doc_search tool
├── test_client.py   # minimal HTTP client
└── docs/            # the corpus (Prefect docs pages)
```

## Roadmap

- [ ] BM25 ranking (`rank_bm25`), so long sections don't win by repetition
- [ ] Embedding search for semantic matches ("retry" ↔ "failure handling")
- [ ] A `get_section(file, heading)` tool so the model can read a full section after searching
- [ ] Cache the index instead of re-reading files on every call

## Credits

Sample docs are © Prefect Technologies and are used here as a test corpus. Source: [docs.prefect.io](https://docs.prefect.io).
