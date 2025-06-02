import asyncio
from crawl4ai import *
import json
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
# 取得首页所有列表，并解析schema，提取数据
async def main():

    # 定义提取策略：解析onclick参数构造实际URL
    schema1 = {
        "name": "DynamicLinkExtractor",
        "baseSelector": "a[onclick^='opendetailjyxx']",  # 匹配所有动态链接
        "fields": [{
            "name": "target_url",
            "type": "attribute",
            "attribute": "onclick",
            "transform": lambda val: f"/detail?uuid="  # 提取onclick参数中的URL
        }]
    }
    schema = {
        "name": "DynamicLinkExtractor",
        "baseSelector": "table",  # 匹配所有动态链接
        "fields": [{
            "name": "target_url",
            "type": "attribute",
            "attribute": "class",
            "transform": lambda val: f"/detail?uuid="  # 提取onclick参数中的URL
        }]
    }
    extraction_strategy = JsonCssExtractionStrategy(schema)

    browser_config = BrowserConfig(headless=True, java_script_enabled=True)

    js_click_tabs = """
    (async () => {
        const tabs = document.querySelectorAll("section.charge-methodology .tabs-menu-3 > div");
        for(let tab of tabs) {
            tab.scrollIntoView();
            tab.click();
            await new Promise(r => setTimeout(r, 500));
        }
    })();
    """
# ##############################
    async with AsyncWebCrawler() as crawler:
        config = CrawlerRunConfig(
        # Force the crawler to wait until images are fully loaded
        wait_for_images=True,

        # Option 1: If you want to automatically scroll the page to load images
        scan_full_page=True,  # 重要Tells the crawler to try scrolling the entire page
        scroll_delay=5,     # Delay (seconds) between scroll steps

        # Option 2: If the site uses a 'Load More' or JS triggers for images,
        # you can also specify js_code or wait_for logic here.

        cache_mode=CacheMode.BYPASS,
        # css_selector = 'ul#showList:nth-of-type(1)',

        extraction_strategy=JsonCssExtractionStrategy(schema),
        # js_code=[js_click_tabs],
        
        verbose=True
    )
        result = await crawler.arun(
            # url="https://www.cqggzy.com/",
            # url="https://news.cqjjnet.com/html/col95569.htm",            
            # url="https://www.cqggzy.com/tzgg/second-page-zytz.html",            
            # url="https://www.cqggzy.com/jyjg/transaction_detail.html",  
            # url="http://127.0.0.1:5500/exam01.html",  
            url = "https://www.cqggzy.com/jyjg/005002/005002001/005002001002/20250530/a530bae8-f474-4fac-b138-54073f9a830e.html",
            config=config
        )

        if not result.success:
            print(f"Crawl failed: {result.error_message}")
            print(f"Status code: {result.status_code}")
        else:
            print(f"Crawl succeeded: {result.success}")

        with open("result01.md", "w", encoding="utf-8") as f:
            f.write(result.markdown)
        
        print(result.markdown)
        print(result.html)

        # 新增逻辑：遍历external键的值，逐行打印每个对象
        if 'external' in result.links:
            for link in result.links['external']:
                print(link)

        companies = json.loads(result.extracted_content)
        print(f"Successfully extracted {len(companies)} companies")
        # print(json.dumps(companies[0], indent=2))
        print(json.dumps(companies))

if __name__ == "__main__":
    asyncio.run(main())
