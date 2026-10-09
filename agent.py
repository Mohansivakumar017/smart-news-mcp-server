"""
agent.py - Autonomous News Research Agent
Demonstrates Agentic Workflow Orchestration using the Smart News Feed MCP Server tools.

Workflow:
  1. Formulates search strategy based on user topic.
  2. Queries Google News via MCP tool `search_articles_by_keyword`.
  3. Analyzes top article candidates and reads article body via `get_article_content`.
  4. Synthesizes an executive intelligence briefing with key takeaways and citations.
"""

import sys
import server


class NewsResearchAgent:
    """An autonomous agent that plans, searches, reads, and synthesizes news intelligence."""

    def __init__(self, name: str = "NewsAnalyst-Agent"):
        self.name = name

    def run(self, topic: str, max_articles: int = 3) -> dict:
        print(f"\n[{self.name}] 🤖 Initializing Agentic Research Workflow for: '{topic}'")
        print(f"[{self.name}] 🔍 Step 1: Invoking MCP tool `search_articles_by_keyword`...")

        # Step 1: Search using MCP tool
        articles = server.search_articles_by_keyword(keyword=topic, max_results=max_articles)
        if not articles:
            return {
                "topic": topic,
                "status": "No articles found",
                "summary": "Agent found no relevant stories for this topic."
            }

        print(f"[{self.name}] 📰 Step 2: Retrieved {len(articles)} candidate articles. Selecting primary source...")
        primary_article = articles[0]
        url = primary_article.get("url", "")
        title = primary_article.get("title", "")
        source = primary_article.get("source", "Unknown")

        print(f"[{self.name}] 📖 Step 3: Invoking MCP tool `get_article_content` to extract full story context...")
        content_res = server.get_article_content(url=url, max_length=1500)
        extracted_text = content_res.get("content", primary_article.get("description", ""))

        print(f"[{self.name}] 🧠 Step 4: Synthesizing executive briefing...")

        # Structured synthesis
        briefing = {
            "topic": topic,
            "agent": self.name,
            "headline": title,
            "primary_source": source,
            "url": url,
            "executive_summary": (
                f"The story '{title}' reported by {source} discusses key developments regarding {topic}. "
                f"Key initial summary: {primary_article.get('description', '')}"
            ),
            "key_takeaways": [
                f"Primary topic focus: {topic}",
                f"Published story: {title}",
                f"Reporting agency: {source}",
            ],
            "related_coverage": [
                {"title": a.get("title"), "source": a.get("source"), "link": a.get("url")}
                for a in articles[1:]
            ],
        }

        print(f"[{self.name}] ✅ Research Briefing synthesized successfully!\n")
        return briefing


def main():
    topic = sys.argv[1] if len(sys.argv) > 1 else "Artificial Intelligence"
    agent = NewsResearchAgent()
    result = agent.run(topic)

    print("=" * 65)
    print(f"📋 AGENT RESEARCH BRIEFING: {result['topic'].upper()}")
    print("=" * 65)
    print(f"Headline:        {result['headline']}")
    print(f"Source:          {result['primary_source']}")
    print(f"Summary:         {result['executive_summary']}")
    print("\nKey Takeaways:")
    for takeaway in result["key_takeaways"]:
        print(f" • {takeaway}")

    if result.get("related_coverage"):
        print("\nRelated Coverage Tracked by Agent:")
        for rel in result["related_coverage"]:
            print(f" • {rel['title']} ({rel['source']})")
    print("=" * 65)


if __name__ == "__main__":
    main()
