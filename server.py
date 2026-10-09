import html
from pathlib import Path
import re
import sys
import time
import urllib.parse
import urllib.request
import feedparser
from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse

# Initialize FastMCP Server
mcp = FastMCP("Smart News Feed MCP Server")

WEB_DIR = Path(__file__).parent / "web"

# In-memory cache (2 minutes TTL) to prevent rate limits
_CACHE: dict[str, tuple[float, list | dict]] = {}
CACHE_TTL_SECONDS = 120

# Standard Google News Category mapping
CATEGORY_MAP = {
    "tech": "TECHNOLOGY",
    "technology": "TECHNOLOGY",
    "business": "BUSINESS",
    "finance": "BUSINESS",
    "science": "SCIENCE",
    "health": "HEALTH",
    "sports": "SPORTS",
    "world": "WORLD",
    "entertainment": "ENTERTAINMENT",
}


def _get_from_cache(key: str) -> list | dict | None:
    """Retrieve entry from in-memory cache if not expired."""
    cached = _CACHE.get(key)
    if cached:
        timestamp, data = cached
        if time.time() - timestamp < CACHE_TTL_SECONDS:
            return data
    return None


def _set_cache(key: str, data: list | dict) -> None:
    """Store entry in in-memory cache."""
    _CACHE[key] = (time.time(), data)


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


def _parse_entries(parsed_feed, max_results: int) -> list[dict]:
    """Helper to convert feedparser entries into clean, token-efficient article dictionaries."""
    results = []
    for entry in parsed_feed.entries[:max_results]:
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
    cache_key = f"headlines_{max_results}"
    cached = _get_from_cache(cache_key)
    if cached is not None:
        return cached

    parsed = feedparser.parse("https://news.google.com/rss")
    results = _parse_entries(parsed, max_results)
    _set_cache(cache_key, results)
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

    cache_key = f"search_{keyword.strip().lower()}_{max_results}"
    cached = _get_from_cache(cache_key)
    if cached is not None:
        return cached

    encoded_query = urllib.parse.quote(keyword.strip())
    search_url = f"https://news.google.com/rss/search?q={encoded_query}"
    parsed = feedparser.parse(search_url)
    results = _parse_entries(parsed, max_results)
    _set_cache(cache_key, results)
    return results


@mcp.tool(
    name="get_news_by_category",
    description="Get top news headlines filtered by standard category (Technology, Business, Science, Health, Sports, World, Entertainment).",
    tags={"news", "category", "topics", "rss", "feed"},
)
def get_news_by_category(category: str, max_results: int = 5) -> list[dict]:
    """
    Get top news headlines filtered by category.

    Args:
        category (str): Category name (e.g., 'technology', 'business', 'science', 'health', 'sports', 'world').
        max_results (int): The maximum number of articles to return (default: 5).

    Returns:
        list[dict]: A list of category news articles with title, url, description, source, and pubDate.
    """
    cat_normalized = category.strip().lower()
    topic = CATEGORY_MAP.get(cat_normalized, category.strip().upper())

    cache_key = f"category_{topic}_{max_results}"
    cached = _get_from_cache(cache_key)
    if cached is not None:
        return cached

    category_url = f"https://news.google.com/rss/headlines/section/topic/{topic}"
    parsed = feedparser.parse(category_url)
    results = _parse_entries(parsed, max_results)
    _set_cache(cache_key, results)
    return results


@mcp.tool(
    name="get_article_content",
    description="Fetch and extract readable text paragraphs from an article URL for in-depth LLM analysis.",
    tags={"article", "content", "reader", "text", "summary"},
)
def get_article_content(url: str, max_length: int = 3000) -> dict:
    """
    Fetch an article web page and extract the clean text body for an LLM to read.

    Args:
        url (str): The web URL of the article to read.
        max_length (int): Maximum character length of the extracted text (default: 3000).

    Returns:
        dict: A dictionary containing title, url, extracted readable content, and paragraph count.
    """
    if not url or not url.strip():
        return {"error": "A valid URL must be provided."}

    cache_key = f"article_{url.strip()}_{max_length}"
    cached = _get_from_cache(cache_key)
    if cached is not None:
        return cached

    try:
        req = urllib.request.Request(
            url.strip(),
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            },
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            content_type = resp.headers.get("Content-Type", "")
            if "text/html" not in content_type and "text/plain" not in content_type:
                return {"error": "URL does not return HTML or plain text", "url": url}
            html_content = resp.read().decode("utf-8", errors="ignore")
            final_url = resp.geturl()

        # Extract page title
        title_match = re.search(r"<title[^>]*>(.*?)</title>", html_content, re.IGNORECASE | re.DOTALL)
        title = html.unescape(title_match.group(1)).strip() if title_match else ""

        # Clean scripts, styles, nav, ads, headers, footers
        cleaned = re.sub(
            r"<(script|style|nav|header|footer|aside|svg)[^>]*>.*?</\1>",
            " ",
            html_content,
            flags=re.DOTALL | re.IGNORECASE,
        )

        # Extract paragraphs
        paragraphs = re.findall(r"<p[^>]*>(.*?)</p>", cleaned, flags=re.DOTALL | re.IGNORECASE)
        clean_paras = []
        for p in paragraphs:
            clean_p = re.sub(r"<[^>]+>", " ", p)
            clean_p = html.unescape(clean_p)
            clean_p = " ".join(clean_p.split())
            if len(clean_p) > 35:
                clean_paras.append(clean_p)

        full_text = "\n\n".join(clean_paras)
        if len(full_text) > max_length:
            full_text = full_text[:max_length] + "... [truncated]"

        result = {
            "url": final_url,
            "title": title,
            "content": full_text if full_text else "No readable paragraph content could be extracted from this page.",
            "paragraph_count": len(clean_paras),
        }
        _set_cache(cache_key, result)
        return result
    except Exception as e:
        return {"error": f"Failed to fetch article: {str(e)}", "url": url}


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


@mcp.custom_route("/api/category", methods=["GET"])
async def api_category(request: Request) -> JSONResponse:
    """HTTP API endpoint to retrieve news by category."""
    category = request.query_params.get("category", "technology")
    max_results = int(request.query_params.get("max_results", 6))
    data = get_news_by_category(category=category, max_results=max_results)
    return JSONResponse(data)


@mcp.custom_route("/api/article", methods=["GET"])
async def api_article(request: Request) -> JSONResponse:
    """HTTP API endpoint to extract readable text from an article URL."""
    url = request.query_params.get("url", "")
    data = get_article_content(url=url)
    return JSONResponse(data)


if __name__ == "__main__":
    try:
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
    except (KeyboardInterrupt, SystemExit):
        print("\n👋 Smart News Feed MCP Server stopped cleanly. Goodbye!\n")
        sys.exit(0)
