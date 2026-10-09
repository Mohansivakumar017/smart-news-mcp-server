# Smart News Feed MCP Server

An MCP server built with FastMCP that parses RSS feeds for LLMs.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![FastMCP](https://img.shields.io/badge/FastMCP-4.1.0-emerald.svg)](https://github.com/jlowin/fastmcp)

---

## 📖 Overview

The **Smart News Feed MCP Server** provides language models and AI agents with real-time access to the latest news headlines, category feeds, keyword search queries, and full article reader tools using Google News RSS feeds. 

Built with the lightweight [FastMCP](https://github.com/jlowin/fastmcp) framework:
* **Token-Efficient**: Automatically strips noisy HTML tags, ads, and markup so LLMs receive clean, concise summaries.
* **Smart Caching**: Includes an in-memory 2-minute cache to prevent duplicate requests and protect against rate-limiting.
* **No API Keys Required**: Uses open syndicated RSS feeds directly.
* **Interactive Web Dashboard**: Includes a live browser UI (`--ui`) for visual inspection and manual testing alongside MCP.

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
> Then open [http://127.0.0.1:8081](http://127.0.0.1:8081) to browse categories, search news, read articles, and view live MCP JSON payloads!

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

---

### 3. `get_news_by_category`
Retrieve top news headlines filtered by standard category topics.

* **Supported Categories:** `technology`, `business`, `science`, `health`, `sports`, `world`, `entertainment`.
* **Parameters:**
  * `category` (*string*, required): Category topic name.
  * `max_results` (*integer*, optional, default: `5`): Maximum number of articles to return.

* **Example Call:**
```json
{
  "name": "get_news_by_category",
  "arguments": {
    "category": "technology",
    "max_results": 2
  }
}
```

---

### 4. `get_article_content`
Fetch and extract clean body paragraphs from any article URL for in-depth LLM analysis and summarization.

* **Parameters:**
  * `url` (*string*, required): Web URL of the article.
  * `max_length` (*integer*, optional, default: `3000`): Maximum character length to return.

* **Example Call:**
```json
{
  "name": "get_article_content",
  "arguments": {
    "url": "https://en.wikipedia.org/wiki/Artificial_intelligence",
    "max_length": 1000
  }
}
```

* **Example Response:**
```json
{
  "title": "Artificial intelligence - Wikipedia",
  "url": "https://en.wikipedia.org/wiki/Artificial_intelligence",
  "paragraph_count": 183,
  "content": "Artificial intelligence (AI) is the capability of computational systems..."
}
```

## 🤖 Autonomous Agentic Workflow

This repository includes an autonomous news research agent ([agent.py](agent.py)) that demonstrates end-to-end agentic workflow orchestration using the MCP tools:

```bash
python agent.py "artificial intelligence"
```

**How the Agent Operates:**
1. **Tool Invocation 1:** Formulates search strategy and queries `search_articles_by_keyword`.
2. **Tool Invocation 2:** Analyzes retrieved candidates and extracts full context via `get_article_content`.
3. **Synthesis:** Synthesizes an executive intelligence briefing with key takeaways, publisher metadata, and related coverage citations.

---

## 🧪 Testing

To run the automated verification test for all 4 tools:

```bash
python test_server.py
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
