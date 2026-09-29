from operator import contains
from pathlib import Path
import re
from fastmcp import FastMCP
import os
from pathlib import Path
    
mcp = FastMCP("Doc Search MCP")

DOCS = Path(__file__).parent / "docs"
STOP = {"how","do","i","a","an","the","to","in","is","what","of","and","for","my","can","does"}

def section(text: str):
    parts = re.split(r"^## +", text, flags=re.MULTILINE)
    if parts[0].strip():
        yield "Introduction", parts[0].strip()
    for part in parts[1:]:
        heading, _, body = part.partition("\n")
        yield heading.strip(), body.strip()

@mcp.tool
def doc_search(query: str, limit: int = 3) -> list[dict]:
    """
    Search the Prefect docs. Scores each ## section by whole-word query hits
    (heading hits count double) and returns the top matches as
    {file, heading, snippet, score}.
    """
    words = [w for w in re.findall(r"\w+", query.lower()) if w not in STOP]   
    if not words:
        return []

    results = []
    for path in DOCS.rglob("*.md"):                                          
        text = path.read_text(encoding="utf-8")
        for heading, body in section(text):
            tokens = re.findall(r"\w+", (heading + " " + body).lower())     
            score = sum(tokens.count(w) for w in words)
            score += 2 * sum(w in heading.lower() for w in words)           
            if score > 0:
                results.append({
                    "file": path.name,                                      
                    "heading": heading,
                    "snippet": body[:400] + ("..." if len(body) > 400 else ""),
                    "score": score,
                })

    results.sort(key=lambda r: r["score"], reverse=True)
    return results[:limit]
    
if __name__ == "__main__":
    mcp.run()


