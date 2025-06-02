import json
# 加入了beautifulsoup4和html2text库，用于处理HTML内容和转换为markdown格式。
import asyncio
from crawl4ai import AsyncWebCrawler
from bs4 import BeautifulSoup
import html2text
import os
from datetime import datetime


def get_urls(json_file_path):
    """
    从指定的JSON文件中获取urls键值
    
    Args:
        json_file_path: JSON文件的路径
        
    Returns:
        list: 包含URL信息的列表
    """
    try:
        # 读取JSON文件
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 获取urls键值
        urls = data.get('urls', [])
        
        print(f"✅ 成功从 {json_file_path} 获取 {len(urls)} 个URL")
        return urls
    
    except Exception as e:
        print(f"❌ 读取文件失败: {json_file_path} - {str(e)}")
        return []
async def crawl_single_webpage_to_markdown(url, source_info=""):
    """
    使用crawl4ai爬取指定网页的mainContent元素并返回markdown格式内容
    """
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
                print(f"✅ 爬取成功! {source_info}")
                print(f"📄 页面标题: {result.metadata.get('title', 'N/A')}")
                print(f"🔗 URL: {url}")
                
                # 从HTML内容中提取mainContent并转换为markdown
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
                    
                    return {
                        'success': True,
                        'source': source_info,
                        'url': url,
                        'title': result.metadata.get('title', 'N/A'),
                        'content': markdown_content,
                        'element_found': True
                    }
                else:
                    print(f"❌ 未找到mainContent元素: {source_info}")
                    return {
                        'success': False,
                        'source': source_info,
                        'url': url,
                        'error': '未找到mainContent元素'
                    }
            else:
                print(f"❌ 爬取失败: {source_info} - {result.error_message}")
                return {
                    'success': False,
                    'source': source_info,
                    'url': url,
                    'error': result.error_message
                }
                
    except Exception as e:
        print(f"❌ 发生错误: {source_info} - {str(e)}")
        return {
            'success': False,
            'source': source_info,
            'url': url,
            'error': str(e)
        }

async def crawl_multiple_webpages_to_markdown(url_list):
    """
    批量爬取多个网页的mainContent元素并返回markdown格式内容
    
    Args:
        url_list: 包含字典的列表，每个字典应包含 'url', 'source', 'name' 等字段
    
    Returns:
        list: 包含爬取结果的列表
    """
    if not url_list:
        print("❌ URL列表为空")
        return []
    
    print(f"🚀 开始批量爬取 {len(url_list)} 个网页的mainContent元素...")
    
    results = []
    all_markdown_content = ""
    
    # 创建输出目录
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"crawl_results_{timestamp}"
    os.makedirs(output_dir, exist_ok=True)
    
    for i, item in enumerate(url_list, 1):
        print(f"\n{'='*60}")
        print(f"处理第 {i}/{len(url_list)} 个URL")
        print(f"来源: {item.get('source', 'Unknown')}")
        print(f"名称: {item.get('name', 'Unknown')}")
        print(f"URL: {item.get('final_url', '')}")
        print(f"{'='*60}")
        
        if not item.get('final_url'):
            print("❌ URL为空，跳过此项")
            results.append({
                'success': False,
                'source': item.get('source', 'Unknown'),
                'name': item.get('name', 'Unknown'),
                'url': '',
                'error': 'URL为空'
            })
            continue
        
        # 爬取单个网页
        result = await crawl_single_webpage_to_markdown(
            item['final_url'],
            f"{item.get('source', 'Unknown')} - {item.get('name', 'Unknown')}"
        )
        
        # 添加额外信息
        result['name'] = item.get('name', 'Unknown')
        results.append(result)
        
        # 如果爬取成功，保存单个文件并添加到总内容中
        if result['success']:
            # 生成安全的文件名
            safe_filename = f"{i:03d}_{item.get('source', 'unknown').replace('/', '_').replace(' ', '_')}"
            file_path = os.path.join(output_dir, f"{safe_filename}.md")
            
            # 构建文件内容
            file_content = f"""# {item.get('name', 'Unknown')}

**来源**: {item.get('source', 'Unknown')}  
**URL**: {item['final_url']}  
**页面标题**: {result['title']}  
**mainContent元素**: {'已找到' if result.get('element_found') else '未找到'}  
**爬取时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

{result['content']}
"""
            
            # 保存单个文件
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(file_content)
            print(f"💾 内容已保存到 {file_path}")
            
            # 添加到总内容中
            all_markdown_content += f"\n\n{'='*80}\n"
            all_markdown_content += file_content
        
        # 添加延迟以避免过于频繁的请求
        await asyncio.sleep(1)
    
    # 保存汇总文件
    summary_file = os.path.join(output_dir, "00_summary.md")
    with open(summary_file, "w", encoding="utf-8") as f:
        f.write(f"""# 批量爬取mainContent汇总报告

**爬取时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**总URL数量**: {len(url_list)}  
**成功数量**: {sum(1 for r in results if r['success'])}  
**失败数量**: {sum(1 for r in results if not r['success'])}  

## 详细结果

""")
        
        for i, result in enumerate(results, 1):
            status = "✅ 成功" if result['success'] else "❌ 失败"
            error_msg = f" - {result.get('error', '')}" if not result['success'] else ""
            f.write(f"{i}. {status} | {result.get('source', 'Unknown')} | {result.get('name', 'Unknown')}{error_msg}\n")
        
        f.write(f"\n---\n\n{all_markdown_content}")
    
    print(f"\n📊 批量爬取完成！")
    print(f"✅ 成功: {sum(1 for r in results if r['success'])}")
    print(f"❌ 失败: {sum(1 for r in results if not r['success'])}")
    print(f"📁 结果保存在目录: {output_dir}")
    print(f"📄 汇总文件: {summary_file}")
    
    return results

# 同步版本函数（如果需要在同步环境中使用）
def crawl_multiple_webpages_sync(url_list):
    """
    同步版本的批量爬取函数
    """
    return asyncio.run(crawl_multiple_webpages_to_markdown(url_list))

# 主函数
async def main():
    """
    主函数，执行批量爬取任务
    """
    # 从JSON文件获取URLs
    json_file_path = 'jyxx_final_urls.json'
    jyxx_urls = get_urls(json_file_path)

    example_urls = [
            {
                "source": "第 1 页第 1 个元素",
                "name": "重庆市三峡库区水源工程智管能力建设先行先试项目（涪陵区）招标计划表",
                "final_url": "https://www.cqggzy.com/jyxx/004002/004002008/20250531/9d76df21-eb96-4384-aa1d-3e1e852cd414.html"
            },
            {
                "source": "第 1 页第 2 个元素",
                "name": "厨房及生活设施设备(WLQ25A00353)询价公告",
                "final_url": "https://www.cqggzy.com/jyxx/004005/004005001/20250531/1504897345949839360.html"
            }
        ]
    
    # 执行批量爬取
    # results = await crawl_multiple_webpages_to_markdown(example_urls)
    results = await crawl_multiple_webpages_to_markdown(jyxx_urls)
    
    return results

# 使用示例
if __name__ == "__main__":
    # 异步运行
    results = asyncio.run(main())
    
    # 或者直接调用批量爬取函数
    # your_url_list = [...]  # 你的URL列表
    # results = crawl_multiple_webpages_sync(your_url_list)