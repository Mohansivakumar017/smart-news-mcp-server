import html
from pathlib import Path
import re
import urllib.parse
import feedparser
from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse

# Initialize FastMCP Server
mcp = FastMCP("Smart News Feed MCP Server")

WEB_DIR = Path(__file__).parent / "web"


def _clean_html(raw_html: str | None) -> str:
    """Helper to strip HTML tags and extract the primary story summary for LLM consumption."""
    if not raw_html:
        return ""
    # Extract only the first story snippet if Google returns an HTML list of related articles
    li_matches = re.findall(r"<li[^>]*>(.*?)</li>", raw_html, flags=re.DOTALL)
    target = li_matches[0] if li_matches else raw_html

    cleaned = re.sub(r"<[^>]+>", " ", target)
    cleaned = html.unescape(cleaned)
    return " ".join(cleaned.split())


def _extract_source_name(entry: dict) -> str:
    """Helper to extract publication source name."""
    source = entry.get("source")
    if isinstance(source, dict):
        return source.get("title", "")
    elif isinstance(source, str):
        return source
    return ""


@mcp.tool(
    name="get_google_news_feed",
    description="Get the latest top headlines and metadata from the Google News RSS feed.",
    tags={"news", "google", "feed", "rss", "headlines"},
)
def get_google_news_feed(max_results: int = 5) -> list[dict]:
    """
    Get the latest top headlines and metadata from the Google News RSS feed.

    Args:
        max_results (int): The maximum number of articles to return (default: 5).

    Returns:
        list[dict]: A list of news articles with title, url, description, source, and pubDate.
    """
    parsed = feedparser.parse("https://news.google.com/rss")
    results = []

    for entry in parsed.entries[:max_results]:
        results.append(
            {
                "title": entry.get("title", ""),
                "url": entry.get("link", ""),
                "description": _clean_html(entry.get("description", "")),
                "source": _extract_source_name(entry),
                "pubDate": entry.get("published", ""),
            }
        )

    return results


@mcp.tool(
    name="search_articles_by_keyword",
    description="Search Google News RSS feed for articles matching a specific keyword or query.",
    tags={"news", "search", "keyword", "rss", "feed"},
)
def search_articles_by_keyword(keyword: str, max_results: int = 5) -> list[dict]:
    """
    Search Google News RSS feed for articles matching a specific keyword or query.

    Args:
        keyword (str): The search term or topic to query news articles for.
        max_results (int): The maximum number of articles to return (default: 5).

    Returns:
        list[dict]: A list of matching news articles with title, url, description, source, and pubDate.
    """
    if not keyword or not keyword.strip():
        return []

    encoded_query = urllib.parse.quote(keyword.strip())
    search_url = f"https://news.google.com/rss/search?q={encoded_query}"
    parsed = feedparser.parse(search_url)
    results = []

    for entry in parsed.entries[:max_results]:
        results.append(
            {
                "title": entry.get("title", ""),
                "url": entry.get("link", ""),
                "description": _clean_html(entry.get("description", "")),
                "source": _extract_source_name(entry),
                "pubDate": entry.get("published", ""),
            }
        )

    return results


# Custom HTTP Routes for Web Demo & API
@mcp.custom_route("/", methods=["GET"])
async def serve_dashboard(request: Request) -> HTMLResponse:
    """Serve the interactive web demo dashboard."""
    index_file = WEB_DIR / "index.html"
    if index_file.exists():
        content = index_file.read_text(encoding="utf-8")
        return HTMLResponse(content)
    return HTMLResponse("<h1>Smart News Feed MCP Server</h1><p>Visit /mcp for MCP endpoint.</p>")


@mcp.custom_route("/api/feed", methods=["GET"])
async def api_feed(request: Request) -> JSONResponse:
    """HTTP API endpoint to retrieve latest top headlines."""
    max_results = int(request.query_params.get("max_results", 6))
    data = get_google_news_feed(max_results=max_results)
    return JSONResponse(data)


@mcp.custom_route("/api/search", methods=["GET"])
async def api_search(request: Request) -> JSONResponse:
    """HTTP API endpoint to search articles by keyword."""
    keyword = request.query_params.get("keyword", "")
    max_results = int(request.query_params.get("max_results", 6))
    data = search_articles_by_keyword(keyword=keyword, max_results=max_results)
    return JSONResponse(data)


if __name__ == "__main__":
    import sys

    if any(arg in sys.argv for arg in ("--ui", "--web", "--http")):
        print("\n" + "=" * 65)
        print("🚀 Smart News Feed MCP Server & Web Demo Dashboard")
        print("=" * 65)
        print("👉 Web UI Dashboard:  http://127.0.0.1:8081")
        print("👉 MCP Endpoint:      http://127.0.0.1:8081/mcp")
        print("=" * 65 + "\n")
        mcp.run(transport="http", host="127.0.0.1", port=8081)
    else:
        mcp.run()
