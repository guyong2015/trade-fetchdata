# 加入了beautifulsoup4和html2text库，用于处理HTML内容和转换为markdown格式。
import asyncio
from crawl4ai import AsyncWebCrawler
from bs4 import BeautifulSoup
import html2text

async def crawl_webpage_to_markdown():
    """
    使用crawl4ai爬取指定网页的mainContent元素并返回markdown格式内容
    """
    url = "https://www.cqggzy.com/jyxx/004002/004002008/20250531/9d76df21-eb96-4384-aa1d-3e1e852cd414.html"
    url = "https://www.cqggzy.com/jyxx/004005/004005001/20250531/1504897345949839360.html"

    # url = "https://www.cqggzy.com/jumpnew.html?infoid=9d76df21-eb96-4384-aa1d-3e1e852cd414&categorynum=004002008"
    try:
        # 创建异步爬虫实例
        async with AsyncWebCrawler(verbose=True) as crawler:
            # 爬取网页
            result = await crawler.arun(
                url=url,
                # 等待mainContent元素加载完成
                wait_for_selector="#mainContent",
                timeout=30000,  # 30秒超时
                # 设置用户代理
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                # 使用CSS选择器只提取mainContent内容
                css_selector="#mainContent"
            )
            
            if result.success:
                print("✅ 爬取成功!")
                print(f"📄 页面标题: {result.metadata.get('title', 'N/A')}")
                print(f"🔗 URL: {url}")
                
                # 从HTML内容中提取mainContent并转换为markdown
                from bs4 import BeautifulSoup
                import html2text
                
                # 解析HTML内容
                soup = BeautifulSoup(result.html, 'html.parser')
                maincontent_element = soup.find(id='mainContent')
                
                if maincontent_element:
                    print("🔍 找到 mainContent 元素")
                    
                    # 设置html2text转换器
                    h = html2text.HTML2Text()
                    h.ignore_links = False
                    h.ignore_images = False
                    h.body_width = 0  # 不限制行宽
                    
                    # 转换mainContent为markdown
                    print("📋 处理 mainContent 元素...")
                    maincontent_html = str(maincontent_element)
                    markdown_content = h.handle(maincontent_html)
                    
                    print(f"📝 转换后内容长度: {len(markdown_content)} 字符")
                    print("\n" + "="*50 + " MAINCONTENT MARKDOWN 内容 " + "="*50)
                    print(markdown_content)
                    print("="*111)
                    
                    # 保存到文件
                    with open("maincontent.md", "w", encoding="utf-8") as f:
                        f.write(markdown_content)
                    print("\n💾 mainContent内容已保存到 maincontent.md 文件")
                    
                    return markdown_content
                else:
                    print("❌ 未找到id='mainContent'的元素")
                    return None
            else:
                print(f"❌ 爬取失败: {result.error_message}")
                return None
                
    except Exception as e:
        print(f"❌ 发生错误: {str(e)}")
        return None

# 同步版本函数（如果需要在同步环境中使用）
def crawl_webpage_sync():
    """
    同步版本的爬取函数
    """
    return asyncio.run(crawl_webpage_to_markdown())

# 主函数
async def main():
    """
    主函数，执行爬取任务
    """
    print("🚀 开始爬取网页的mainContent元素...")
    markdown_content = await crawl_webpage_to_markdown()
    
    if markdown_content:
        print("\n✅ mainContent元素爬取完成!")
    else:
        print("\n❌ mainContent元素爬取失败!")

# 运行示例
if __name__ == "__main__":
    # 异步运行
    asyncio.run(main())
    
    # 或者使用同步版本
    # crawl_webpage_sync()