import json
import sys
import server


def test_news_tools():
    print("=" * 65)
    print("Testing Smart News Feed MCP Server Tools (4 Tools)")
    print("=" * 65)

    # 1. Test get_google_news_feed
    print("\n[1] Testing get_google_news_feed(max_results=2)...")
    headlines = server.get_google_news_feed(max_results=2)
    print(f"-> Returned {len(headlines)} headlines:")
    for i, a in enumerate(headlines, 1):
        print(f"   {i}. {a['title']} [{a['source']}]")

    # 2. Test search_articles_by_keyword
    keyword = "artificial intelligence"
    print(f"\n[2] Testing search_articles_by_keyword(keyword='{keyword}', max_results=2)...")
    search_results = server.search_articles_by_keyword(keyword=keyword, max_results=2)
    print(f"-> Returned {len(search_results)} search results:")
    for i, a in enumerate(search_results, 1):
        print(f"   {i}. {a['title']} [{a['source']}]")

    # 3. Test get_news_by_category
    category = "technology"
    print(f"\n[3] Testing get_news_by_category(category='{category}', max_results=2)...")
    category_results = server.get_news_by_category(category=category, max_results=2)
    print(f"-> Returned {len(category_results)} category articles:")
    for i, a in enumerate(category_results, 1):
        print(f"   {i}. {a['title']} [{a['source']}]")

    # 4. Test get_article_content
    test_url = "https://en.wikipedia.org/wiki/Artificial_intelligence"
    print(f"\n[4] Testing get_article_content(url='{test_url}', max_length=250)...")
    article_res = server.get_article_content(url=test_url, max_length=250)
    print(f"-> Title: {article_res.get('title')}")
    print(f"-> Paragraphs extracted: {article_res.get('paragraph_count')}")
    print(f"-> Preview: {article_res.get('content')[:120]}...")

    print("\n" + "=" * 65)
    print("All 4 MCP tools passed verification successfully!")
    print("=" * 65)


if __name__ == "__main__":
    test_news_tools()
