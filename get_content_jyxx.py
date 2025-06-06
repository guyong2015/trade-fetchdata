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

def save_batch_results(results, output_dir, batch_num, start_index):
    """
    保存批次结果到文件
    
    Args:
        results: 爬取结果列表
        output_dir: 输出目录
        batch_num: 批次号
        start_index: 起始索引
    """
    batch_dir = os.path.join(output_dir, f"batch_{batch_num:03d}")
    os.makedirs(batch_dir, exist_ok=True)
    
    batch_content = ""
    successful_count = 0
    
    for i, result in enumerate(results):
        file_index = start_index + i + 1
        
        if result['success']:
            successful_count += 1
            # 生成安全的文件名
            safe_filename = f"{file_index:03d}_{result.get('source', 'unknown').replace('/', '_').replace(' ', '_')}"
            file_path = os.path.join(batch_dir, f"{safe_filename}.md")
            
            # 构建文件内容
            file_content = f"""# {result.get('name', 'Unknown')}

**来源**: {result.get('source', 'Unknown')}  
**URL**: {result['url']}  
**页面标题**: {result['title']}  
**mainContent元素**: {'已找到' if result.get('element_found') else '未找到'}  
**爬取时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

{result['content']}
"""
            
            # 保存单个文件
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(file_content)
            
            # 添加到批次汇总内容中
            batch_content += f"\n\n{'='*80}\n"
            batch_content += file_content
    
    # 保存批次汇总文件
    batch_summary_file = os.path.join(batch_dir, f"batch_{batch_num:03d}_summary.md")
    with open(batch_summary_file, "w", encoding="utf-8") as f:
        f.write(f"""# 批次 {batch_num} 爬取结果汇总

**批次号**: {batch_num}  
**处理范围**: {start_index + 1} - {start_index + len(results)}  
**爬取时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**批次URL数量**: {len(results)}  
**成功数量**: {successful_count}  
**失败数量**: {len(results) - successful_count}  

## 详细结果

""")
        
        for i, result in enumerate(results):
            status = "✅ 成功" if result['success'] else "❌ 失败"
            error_msg = f" - {result.get('error', '')}" if not result['success'] else ""
            f.write(f"{start_index + i + 1}. {status} | {result.get('source', 'Unknown')} | {result.get('name', 'Unknown')}{error_msg}\n")
        
        f.write(f"\n---\n\n{batch_content}")
    
    print(f"💾 批次 {batch_num} 结果已保存到 {batch_dir}")
    return successful_count

def save_progress_log(output_dir, processed_count, total_count, successful_count, failed_count):
    """
    保存进度日志
    """
    progress_file = os.path.join(output_dir, "progress_log.json")
    progress_data = {
        "last_update": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "processed_count": processed_count,
        "total_count": total_count,
        "successful_count": successful_count,
        "failed_count": failed_count,
        "progress_percentage": round((processed_count / total_count) * 100, 2) if total_count > 0 else 0
    }
    
    with open(progress_file, "w", encoding="utf-8") as f:
        json.dump(progress_data, f, ensure_ascii=False, indent=2)

async def crawl_multiple_webpages_to_markdown(url_list, batch_size=50):
    """
    批量爬取多个网页的mainContent元素并返回markdown格式内容
    每处理指定数量的URL后进行一次文件保存操作
    
    Args:
        url_list: 包含字典的列表，每个字典应包含 'url', 'source', 'name' 等字段
        batch_size: 批次大小，默认50个URL一批
    
    Returns:
        list: 包含爬取结果的列表
    """
    if not url_list:
        print("❌ URL列表为空")
        return []
    
    print(f"🚀 开始批量爬取 {len(url_list)} 个网页的mainContent元素...")
    print(f"📦 批次大小: {batch_size} 个URL/批次")
    
    all_results = []
    total_successful = 0
    total_failed = 0
    
    # 创建输出目录
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"crawl_results_{timestamp}"
    os.makedirs(output_dir, exist_ok=True)
    
    # 分批处理URL
    total_batches = (len(url_list) + batch_size - 1) // batch_size
    
    for batch_num in range(total_batches):
        start_index = batch_num * batch_size
        end_index = min(start_index + batch_size, len(url_list))
        current_batch = url_list[start_index:end_index]
        
        print(f"\n{'='*80}")
        print(f"🔄 处理批次 {batch_num + 1}/{total_batches}")
        print(f"📋 URL范围: {start_index + 1} - {end_index}")
        print(f"📊 当前批次大小: {len(current_batch)}")
        print(f"{'='*80}")
        
        batch_results = []
        
        # 处理当前批次的每个URL
        for i, item in enumerate(current_batch):
            global_index = start_index + i + 1
            print(f"\n{'.'*60}")
            print(f"处理第 {global_index}/{len(url_list)} 个URL (批次内第 {i+1}/{len(current_batch)} 个)")
            print(f"来源: {item.get('source', 'Unknown')}")
            print(f"名称: {item.get('name', 'Unknown')}")
            print(f"URL: {item.get('final_url', '')}")
            print(f"{'.'*60}")
            
            if not item.get('final_url'):
                print("❌ URL为空，跳过此项")
                result = {
                    'success': False,
                    'source': item.get('source', 'Unknown'),
                    'name': item.get('name', 'Unknown'),
                    'url': '',
                    'error': 'URL为空'
                }
                batch_results.append(result)
                total_failed += 1
                continue
            
            # 爬取单个网页
            result = await crawl_single_webpage_to_markdown(
                item['final_url'],
                f"{item.get('source', 'Unknown')} - {item.get('name', 'Unknown')}"
            )
            
            # 添加额外信息
            result['name'] = item.get('name', 'Unknown')
            batch_results.append(result)
            
            if result['success']:
                total_successful += 1
            else:
                total_failed += 1
            
            # 添加延迟以避免过于频繁的请求
            await asyncio.sleep(1)
        
        # 保存当前批次的结果
        batch_successful = save_batch_results(batch_results, output_dir, batch_num + 1, start_index)
        all_results.extend(batch_results)
        
        # 更新进度日志
        processed_count = end_index
        save_progress_log(output_dir, processed_count, len(url_list), total_successful, total_failed)
        
        print(f"\n📊 批次 {batch_num + 1} 完成统计:")
        print(f"✅ 批次成功: {batch_successful}")
        print(f"❌ 批次失败: {len(batch_results) - batch_successful}")
        print(f"📈 总体进度: {processed_count}/{len(url_list)} ({(processed_count/len(url_list)*100):.1f}%)")
        print(f"📊 累计成功: {total_successful}")
        print(f"📊 累计失败: {total_failed}")
        
        # 批次间稍作停顿
        if batch_num < total_batches - 1:
            print("⏸️  批次间暂停 3 秒...")
            await asyncio.sleep(3)
    
    # 生成最终汇总报告
    final_summary_file = os.path.join(output_dir, "00_FINAL_SUMMARY.md")
    with open(final_summary_file, "w", encoding="utf-8") as f:
        f.write(f"""# 🎉 最终爬取汇总报告

**爬取开始时间**: {timestamp}  
**爬取完成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**总URL数量**: {len(url_list)}  
**批次数量**: {total_batches}  
**批次大小**: {batch_size}  
**✅ 总成功数量**: {total_successful}  
**❌ 总失败数量**: {total_failed}  
**成功率**: {(total_successful/len(url_list)*100):.2f}%

## 📁 文件结构说明

- `00_FINAL_SUMMARY.md` - 本文件，最终汇总报告
- `progress_log.json` - 进度日志文件
- `batch_001/` - 第1批次结果 (URL 1-{min(batch_size, len(url_list))})
- `batch_002/` - 第2批次结果 (URL {batch_size+1}-{min(batch_size*2, len(url_list))})
- ... 依此类推

每个批次目录包含:
- `batch_XXX_summary.md` - 批次汇总文件
- `001_xxx.md`, `002_xxx.md` - 单个URL的爬取结果

## 📊 详细结果统计

""")
        
        # 按批次统计
        for batch_num in range(total_batches):
            start_idx = batch_num * batch_size
            end_idx = min(start_idx + batch_size, len(url_list))
            batch_results = all_results[start_idx:end_idx]
            batch_success = sum(1 for r in batch_results if r['success'])
            batch_fail = len(batch_results) - batch_success
            
            f.write(f"### 批次 {batch_num + 1} (URL {start_idx + 1}-{end_idx})\n")
            f.write(f"- ✅ 成功: {batch_success}\n")
            f.write(f"- ❌ 失败: {batch_fail}\n")
            f.write(f"- 📁 目录: `batch_{batch_num + 1:03d}/`\n\n")
        
        f.write("## 🔍 失败URL详情\n\n")
        failed_count = 0
        for i, result in enumerate(all_results, 1):
            if not result['success']:
                failed_count += 1
                f.write(f"{failed_count}. **{result.get('name', 'Unknown')}**\n")
                f.write(f"   - 来源: {result.get('source', 'Unknown')}\n")
                f.write(f"   - URL: {result.get('url', '')}\n")
                f.write(f"   - 错误: {result.get('error', '')}\n\n")
    
    print(f"\n🎉 批量爬取全部完成！")
    print(f"📊 最终统计:")
    print(f"   总数量: {len(url_list)}")
    print(f"   ✅ 成功: {total_successful}")
    print(f"   ❌ 失败: {total_failed}")
    print(f"   📈 成功率: {(total_successful/len(url_list)*100):.2f}%")
    print(f"   🗂️  批次数: {total_batches}")
    print(f"📁 结果保存在目录: {output_dir}")
    print(f"📄 最终汇总文件: {final_summary_file}")
    
    return all_results

# 同步版本函数（如果需要在同步环境中使用）
def crawl_multiple_webpages_sync(url_list, batch_size=50):
    """
    同步版本的批量爬取函数
    """
    return asyncio.run(crawl_multiple_webpages_to_markdown(url_list, batch_size))

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
    
    # 执行批量爬取，可以自定义批次大小
    # results = await crawl_multiple_webpages_to_markdown(example_urls, batch_size=50)
    results = await crawl_multiple_webpages_to_markdown(jyxx_urls, batch_size=5)
    
    return results

# 使用示例
if __name__ == "__main__":
    # 异步运行
    results = asyncio.run(main())
    
    # 或者直接调用批量爬取函数
    # your_url_list = [...]  # 你的URL列表
    # results = crawl_multiple_webpages_sync(your_url_list, batch_size=50)