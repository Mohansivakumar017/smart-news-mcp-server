# Smart News Feed MCP Server

An MCP server built with FastMCP that parses RSS feeds for LLMs.

---

## 📖 Overview

The **Smart News Feed MCP Server** provides language models with real-time access to the latest news headlines and topic-specific search queries using Google News RSS feeds. Built with the lightweight [FastMCP](https://github.com/jlowin/fastmcp) framework, it automatically formats and strips noisy HTML markup from feed descriptions so LLMs receive clean, token-efficient summaries.

---

## ⚙️ Setup

Install the required dependencies and start the server:

```bash
pip install fastmcp feedparser
python server.py
```

> **Note for Virtual Environments (Linux / macOS):**
> If using the local virtual environment:
> ```bash
> source .venv/bin/activate
> python server.py
> ```

> **Interactive Web Demo Dashboard:**
> To launch the visual news card dashboard & live MCP explorer in your browser:
> ```bash
> python server.py --ui
> ```
> Then open [http://127.0.0.1:8081](http://127.0.0.1:8081) to search news and view live MCP JSON payloads!

---

## 🚀 Configuration for MCP Clients

Add the server to your MCP client configuration (e.g. `claude_desktop_config.json` or any MCP host):

```json
{
  "mcpServers": {
    "smart-news": {
      "command": "python",
      "args": ["/path/to/smart-news-mcp-server/server.py"]
    }
  }
}
```

---

## 🛠️ Tools & Usage

### 1. `get_google_news_feed`
Fetch the latest top headlines and metadata from the Google News RSS feed.

* **Parameters:**
  * `max_results` (*integer*, optional, default: `5`): Maximum number of articles to return.

* **Example Call:**
```json
{
  "name": "get_google_news_feed",
  "arguments": {
    "max_results": 3
  }
}
```

* **Example Response:**
```json
[
  {
    "title": "NASA Rover Finds Surprising Evidence of Ancient Water on Mars",
    "url": "https://news.google.com/rss/articles/...",
    "description": "Perseverance team uncovers geological formations suggesting sustained surface water.",
    "source": "NASA JPL",
    "pubDate": "Fri, 09 Oct 2026 08:30:00 GMT"
  }
]
```

---

### 2. `search_articles_by_keyword`
Search Google News RSS feed for articles matching a specific topic, keyword, or query phrase.

* **Parameters:**
  * `keyword` (*string*, required): Search term or topic query (e.g., `"artificial intelligence"`, `"space exploration"`, `"renewable energy"`).
  * `max_results` (*integer*, optional, default: `5`): Maximum number of articles to return.

* **Example Call:**
```json
{
  "name": "search_articles_by_keyword",
  "arguments": {
    "keyword": "artificial intelligence",
    "max_results": 2
  }
}
```

* **Example Response:**
```json
[
  {
    "title": "Advancements in Generative AI Benchmark Models Announced",
    "url": "https://news.google.com/rss/articles/...",
    "description": "Researchers introduce multimodal reasoning benchmarks with real-time inference.",
    "source": "TechCrunch",
    "pubDate": "Fri, 09 Oct 2026 09:15:00 GMT"
  }
]
```
