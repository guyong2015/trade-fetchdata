import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy
from crawl4ai.content_scraping_strategy import LXMLWebScrapingStrategy
from crawl4ai import *
# filter_chain=FilterChain([url_filter]),指定爬取url中blxw的页面
async def main():
    url_filter = URLPatternFilter(patterns=["*blxw*", "*html*"])
    # Configure a 2-level deep crawl
    config = CrawlerRunConfig(
        deep_crawl_strategy=BFSDeepCrawlStrategy(
            max_depth=1, 
            include_external=False,
            filter_chain=FilterChain([url_filter]),
            max_pages=10
        ),
        scraping_strategy=LXMLWebScrapingStrategy(),
        cache_mode=CacheMode.BYPASS,
        wait_for_images=True,
        scan_full_page=True,
        # css_selector = 'ul#showList:nth-of-type(1)',
        scroll_delay=2, 
        verbose=True
    )

    async with AsyncWebCrawler() as crawler:
        results = await crawler.arun("https://www.cqggzy.com/jyjg/transaction_detail.html", config=config)

        print(f"Crawled {len(results)} pages in total")

        # Access individual results
        for result in results[:5]:  # Show first 3 results
            print(f"URL: {result.url}")
            print(f"Depth: {result.metadata.get('depth', 0)}")

if __name__ == "__main__":
    asyncio.run(main())
