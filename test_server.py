import json
import sys
import server


def test_news_tools():
    print("=" * 60)
    print("Testing Smart News Feed MCP Server Tools")
    print("=" * 60)

    # 1. Test get_google_news_feed
    print("\n[1] Testing get_google_news_feed(max_results=2)...")
    headlines = server.get_google_news_feed(max_results=2)
    print(f"-> Returned {len(headlines)} headlines:")
    for i, article in enumerate(headlines, 1):
        print(f"   {i}. {article['title']} ({article['source']})")
        print(f"      Published: {article['pubDate']}")
        print(f"      Link: {article['url']}")

    # 2. Test search_articles_by_keyword
    keyword = "artificial intelligence"
    print(f"\n[2] Testing search_articles_by_keyword(keyword='{keyword}', max_results=2)...")
    search_results = server.search_articles_by_keyword(keyword=keyword, max_results=2)
    print(f"-> Returned {len(search_results)} search results:")
    for i, article in enumerate(search_results, 1):
        print(f"   {i}. {article['title']} ({article['source']})")
        print(f"      Published: {article['pubDate']}")
        print(f"      Link: {article['url']}")

    print("\n" + "=" * 60)
    print("All tool tests completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    test_news_tools()
