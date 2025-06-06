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
            safe_filename = f"{file_index:03d}_{result.get('name', 'unknown').replace('/', '_').replace(' ', '_')}" # Use name for filename
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

def save_progress_log(output_dir, processed_count, total_count, successful_count, failed_count, start_time=None, end_time=None):
    """
    保存进度日志
    """
    progress_file = os.path.join(output_dir, "progress_log.json")
    
    # 如果文件已存在，先读取原有数据以保留开始时间
    existing_data = {}
    if os.path.exists(progress_file):
        try:
            with open(progress_file, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
        except:
            pass
    
    progress_data = {
        "start_time": start_time or existing_data.get("start_time"),
        "end_time": end_time,
        "last_update": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "processed_count": processed_count,
        "total_count": total_count,
        "successful_count": successful_count,
        "failed_count": failed_count,
        "progress_percentage": round((processed_count / total_count) * 100, 2) if total_count > 0 else 0,
        "is_completed": processed_count >= total_count
    }
    
    # 如果有开始和结束时间，计算总耗时
    if progress_data["start_time"] and progress_data["end_time"]:
        try:
            start_dt = datetime.strptime(progress_data["start_time"], '%Y-%m-%d %H:%M:%S')
            end_dt = datetime.strptime(progress_data["end_time"], '%Y-%m-%d %H:%M:%S')
            duration = end_dt - start_dt
            progress_data["total_duration_seconds"] = int(duration.total_seconds())
            progress_data["total_duration_formatted"] = str(duration).split('.')[0]  # 去掉微秒
        except:
            pass
    
    with open(progress_file, "w", encoding="utf-8") as f:
        json.dump(progress_data, f, ensure_ascii=False, indent=2)

def update_overall_summary(output_dir, all_results, total_successful, total_failed, current_batch, total_batches, batch_size, start_time):
    """
    更新总体汇总报告 (00_OVERALL_SUMMARY.md) - 实时进度报告
    """
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    processed_count = len(all_results)
    total_urls = len(all_results) if all_results else 0 # Use len(all_results) for processed count, total_urls for total
    
    # 读取进度日志获取耗时信息
    progress_file = os.path.join(output_dir, "progress_log.json")
    duration_info = ""
    is_completed = current_batch >= total_batches
    
    if os.path.exists(progress_file):
        try:
            with open(progress_file, "r", encoding="utf-8") as f:
                progress_data = json.load(f)
                if progress_data.get("total_duration_formatted"):
                    duration_info = f"**总耗时**: {progress_data['total_duration_formatted']}  \n"
                elif progress_data.get("start_time"):
                    # 计算当前耗时
                    try:
                        start_dt = datetime.strptime(progress_data["start_time"], '%Y-%m-%d %H:%M:%S')
                        current_dt = datetime.now()
                        current_duration = current_dt - start_dt
                        duration_info = f"**当前耗时**: {str(current_duration).split('.')[0]}  \n"
                    except:
                        pass
        except:
            pass
    
    summary_file = os.path.join(output_dir, "00_OVERALL_SUMMARY.md")
    
    with open(summary_file, "w", encoding="utf-8") as f:
        status_emoji = "🎉" if is_completed and processed_count == total_urls else "🔄"
        status_text = "最终爬取汇总报告" if is_completed and processed_count == total_urls else "实时爬取进度报告"
        
        f.write(f"""# {status_emoji} {status_text}

**爬取开始时间**: {start_time}  
**最后更新时间**: {current_time}  
{duration_info}**总URL数量**: {total_urls}  
**已处理URL数量**: {processed_count}  
**已完成批次**: {current_batch}/{total_batches}  
**批次大小**: {batch_size}  
**✅ 总成功数量**: {total_successful}  
**❌ 总失败数量**: {total_failed}  
**当前成功率**: {(total_successful/processed_count*100):.2f}% (基于已处理的URL)
**整体进度**: {(processed_count/total_urls*100):.1f}%
""")
        
        # Add file structure explanation only once at the beginning or when completed
        if is_completed and processed_count == total_urls:
            f.write("""
## 📁 文件结构说明

- `00_OVERALL_SUMMARY.md` - 本文件，总体汇总报告（实时更新）
- `00_FINAL_SUMMARY.md` - 最终汇总报告（每批次更新）
- `progress_log.json` - 详细进度日志文件
""")
        else:
            f.write("""
## 📁 文件结构说明 (实时更新)

- `00_OVERALL_SUMMARY.md` - 本文件，总体汇总报告（实时更新）
- `00_FINAL_SUMMARY.md` - 最终汇总报告（每批次更新）
- `progress_log.json` - 详细进度日志文件
""")

        f.write("\n## 📊 批次处理状态\n\n")
        # 按批次显示进度
        for batch_num_iter in range(1, total_batches + 1):
            start_idx = (batch_num_iter - 1) * batch_size
            end_idx = min(start_idx + batch_size, total_urls) # Use total_urls for accurate range
            
            if batch_num_iter <= current_batch:
                # 已完成的批次
                batch_results_for_status = [r for r in all_results if r.get('batch_num') == batch_num_iter]
                if batch_results_for_status:
                    batch_success = sum(1 for r in batch_results_for_status if r.get('success', False))
                    batch_fail = len(batch_results_for_status) - batch_success
                    f.write(f"- ✅ 批次 {batch_num_iter} (URL {start_idx + 1}-{end_idx}) - 成功:{batch_success}, 失败:{batch_fail} - `batch_{batch_num_iter:03d}/`\n")
                else:
                    # This case might happen if all_results is not fully populated yet for the batch,
                    # but the batch_num_iter is <= current_batch.
                    # It's safer to just state it's completed.
                    f.write(f"- ✅ 批次 {batch_num_iter} (URL {start_idx + 1}-{end_idx}) - 已完成 - `batch_{batch_num_iter:03d}/`\n")
            elif batch_num_iter == current_batch + 1:
                # 正在处理的批次
                f.write(f"- 🔄 批次 {batch_num_iter} (URL {start_idx + 1}-{end_idx}) - 处理中...\n")
            else:
                # 待处理的批次
                f.write(f"- ⏳ 批次 {batch_num_iter} (URL {start_idx + 1}-{end_idx}) - 等待处理\n")
        
        # 如果有失败的URL，显示失败详情
        if all_results:
            failed_results = [r for r in all_results if not r.get('success', False)]
            if failed_results:
                f.write(f"\n## 🔍 失败URL详情 (共{len(failed_results)}个)\n\n")
                for i, result in enumerate(failed_results, 1):
                    f.write(f"{i}. **{result.get('name', 'Unknown')}**\n")
                    f.write(f"   - 来源: {result.get('source', 'Unknown')}\n")
                    f.write(f"   - URL: {result.get('url', '')}\n")
                    f.write(f"   - 错误: {result.get('error', '')}\n\n")
        
        if is_completed and processed_count == total_urls:
            f.write(f"\n---\n\n## 🎊 爬取任务已全部完成！\n\n")
            f.write(f"感谢您的耐心等待，所有 {processed_count} 个URL已处理完毕。\n")
            f.write(f"详细结果请查看各批次目录中的文件。\n")
        else:
            f.write(f"\n---\n\n## ⏱️ 任务进行中...\n\n")
            f.write(f"当前正在处理第 {current_batch + 1} 批次，请耐心等待。\n")
            f.write(f"您可以随时查看此文件了解最新进度。\n")


def generate_final_summary_report(output_dir, all_results, total_successful, total_failed, url_list_original, batch_size, start_time, current_end_time):
    """
    生成或更新最终汇总报告 (00_FINAL_SUMMARY.md)
    这个报告会随着每批次处理完成而更新，反映当前的累计结果。
    """
    total_urls = len(url_list_original)
    processed_urls_count = len(all_results)
    total_batches = (total_urls + batch_size - 1) // batch_size

    final_summary_file = os.path.join(output_dir, "00_FINAL_SUMMARY.md")

    # Read progress log to get duration info
    progress_file = os.path.join(output_dir, "progress_log.json")
    duration_info = ""
    is_completed = processed_urls_count >= total_urls # Check if all URLs are processed
    
    if os.path.exists(progress_file):
        try:
            with open(progress_file, "r", encoding="utf-8") as f:
                progress_data = json.load(f)
                if progress_data.get("total_duration_formatted"):
                    duration_info = f"**总耗时**: {progress_data['total_duration_formatted']}  \n"
                elif progress_data.get("start_time") and current_end_time:
                    try:
                        start_dt = datetime.strptime(progress_data["start_time"], '%Y-%m-%d %H:%M:%S')
                        current_dt = datetime.strptime(current_end_time, '%Y-%m-%d %H:%M:%S')
                        current_duration = current_dt - start_dt
                        duration_info = f"**当前累计耗时**: {str(current_duration).split('.')[0]}  \n"
                    except:
                        pass
        except:
            pass

    with open(final_summary_file, "w", encoding="utf-8") as f:
        status_emoji = "🎉" if is_completed else "📊"
        status_text = "最终爬取汇总报告" if is_completed else "累计爬取汇总报告 (实时更新)"

        f.write(f"""# {status_emoji} {status_text}

**爬取开始时间**: {start_time}  
**报告生成时间**: {current_end_time}  
{duration_info}**总URL数量**: {total_urls}  
**已处理URL数量**: {processed_urls_count}  
**批次数量**: {total_batches}  
**批次大小**: {batch_size}  
**✅ 总成功数量**: {total_successful}  
**❌ 总失败数量**: {total_failed}  
**成功率**: {(total_successful/processed_urls_count*100):.2f}% (基于已处理的URL)

## 📁 文件结构说明

- `00_OVERALL_SUMMARY.md` - 总体汇总报告（实时进度）
- `00_FINAL_SUMMARY.md` - 本文件，累计/最终汇总报告
- `progress_log.json` - 进度日志文件
- `batch_001/` - 第1批次结果
- `batch_002/` - 第2批次结果
- ... 依此类推

每个批次目录包含:
- `batch_XXX_summary.md` - 批次汇总文件
- `001_xxx.md`, `002_xxx.md` - 单个URL的爬取结果

## 📊 详细结果统计 (基于已处理的URL)

""")
        
        # Group results by batch for accurate statistics
        batch_wise_results = {}
        for result in all_results:
            batch_num = result.get('batch_num')
            if batch_num not in batch_wise_results:
                batch_wise_results[batch_num] = []
            batch_wise_results[batch_num].append(result)

        for batch_num in sorted(batch_wise_results.keys()):
            batch_results = batch_wise_results[batch_num]
            batch_success = sum(1 for r in batch_results if r['success'])
            batch_fail = len(batch_results) - batch_success
            
            # Calculate original URL range for the batch
            start_idx_original = (batch_num - 1) * batch_size
            end_idx_original = min(start_idx_original + batch_size, total_urls)

            f.write(f"### 批次 {batch_num} (URL {start_idx_original + 1}-{end_idx_original})\n")
            f.write(f"- ✅ 成功: {batch_success}\n")
            f.write(f"- ❌ 失败: {batch_fail}\n")
            f.write(f"- 📁 目录: `batch_{batch_num:03d}/`\n\n")
        
        # New section for individual URL details including content
        f.write("## 📋 所有URL详细内容 (累计)\n\n") # Changed title to reflect cumulative content
        
        cumulative_content_for_final_report = ""
        for i, result in enumerate(all_results, 1):
            # Construct content similar to how individual batch files are made
            if result['success']:
                cumulative_content_for_final_report += f"""# {result.get('name', 'Unknown')}

**来源**: {result.get('source', 'Unknown')}  
**URL**: {result['url']}  
**页面标题**: {result['title']}  
**mainContent元素**: {'已找到' if result.get('element_found') else '未找到'}  
**爬取时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

{result['content']}
"""
            else:
                # For failed items, include their details and error, but no content
                cumulative_content_for_final_report += f"""# ❌ 爬取失败: {result.get('name', 'Unknown')}

**来源**: {result.get('source', 'Unknown')}  
**URL**: {result['url']}  
**错误**: {result.get('error', '未知错误')}  
**爬取时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---
"""
            
            # Add a strong separator between each URL's details
            if i < len(all_results):
                cumulative_content_for_final_report += f"\n\n{'='*80}\n\n" # Stronger separator for cumulative report

        f.write(cumulative_content_for_final_report) # Write the accumulated content


        if is_completed:
            f.write(f"\n---\n\n## 🎊 爬取任务已全部完成！\n\n")
            f.write(f"感谢您的耐心等待，所有 {processed_urls_count} 个URL已处理完毕。\n")
            f.write(f"详细结果请查看各批次目录中的文件。\n")
        else:
            f.write(f"\n---\n\n## ⏱️ 任务进行中...\n\n")
            f.write(f"此报告将随每个批次的完成而更新，反映当前的累计结果。\n")
            f.write(f"您可以查看 `00_OVERALL_SUMMARY.md` 获取更实时的进度。\n")


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
    start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    output_dir = f"crawl_results_{timestamp}"
    os.makedirs(output_dir, exist_ok=True)
    
    # 初始化进度日志，记录开始时间
    save_progress_log(output_dir, 0, len(url_list), 0, 0, start_time=start_time)
    
    # 分批处理URL
    total_batches = (len(url_list) + batch_size - 1) // batch_size
    
    for batch_num in range(total_batches):
        start_index = batch_num * batch_size
        end_index = min(start_index + batch_size, len(url_list))
        current_batch_urls = url_list[start_index:end_index] # Renamed to avoid confusion with batch_results
        
        print(f"\n{'='*80}")
        print(f"🔄 处理批次 {batch_num + 1}/{total_batches}")
        print(f"📋 URL范围: {start_index + 1} - {end_index}")
        print(f"📊 当前批次大小: {len(current_batch_urls)}")
        print(f"{'='*80}")
        
        batch_results = []
        
        # 处理当前批次的每个URL
        for i, item in enumerate(current_batch_urls):
            global_index = start_index + i + 1
            print(f"\n{'.'*60}")
            print(f"处理第 {global_index}/{len(url_list)} 个URL (批次内第 {i+1}/{len(current_batch_urls)} 个)")
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
                    'error': 'URL为空',
                    'batch_num': batch_num + 1 # Add batch number to result
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
            result['batch_num'] = batch_num + 1 # Add batch number to result
            batch_results.append(result)
            
            if result['success']:
                total_successful += 1
            else:
                total_failed += 1
            
            # 添加延迟以避免过于频繁的请求
            await asyncio.sleep(1)
        
        # 保存当前批次的结果
        batch_successful = save_batch_results(batch_results, output_dir, batch_num + 1, start_index)
        all_results.extend(batch_results) # Accumulate all results
        
        # Update progress log
        processed_count = end_index
        is_final_batch = (batch_num == total_batches - 1)
        current_end_time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        save_progress_log(output_dir, processed_count, len(url_list), total_successful, total_failed, end_time=current_end_time_str if is_final_batch else None)
        
        # Update overall summary (real-time progress report)
        update_overall_summary(output_dir, all_results, total_successful, total_failed, batch_num + 1, total_batches, batch_size, start_time)

        # Update final summary report (cumulative report) after each batch
        generate_final_summary_report(output_dir, all_results, total_successful, total_failed, url_list, batch_size, start_time, current_end_time_str)
        
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
    
    # Final update to progress log and summary reports after all batches are done
    final_end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    save_progress_log(output_dir, len(url_list), len(url_list), total_successful, total_failed, end_time=final_end_time)
    update_overall_summary(output_dir, all_results, total_successful, total_failed, total_batches, total_batches, batch_size, start_time)
    generate_final_summary_report(output_dir, all_results, total_successful, total_failed, url_list, batch_size, start_time, final_end_time) # Final call for the final report

    print(f"\n🎉 批量爬取全部完成！")
    print(f"📊 最终统计:")
    print(f"   总数量: {len(url_list)}")
    print(f"   ✅ 成功: {total_successful}")
    print(f"   ❌ 失败: {total_failed}")
    print(f"   📈 成功率: {(total_successful/len(url_list)*100):.2f}%")
    print(f"   🗂️  批次数: {total_batches}")
    print(f"📁 结果保存在目录: {output_dir}")
    print(f"📄 总体汇总文件: {os.path.join(output_dir, '00_OVERALL_SUMMARY.md')}")
    print(f"📄 最终详细报告: {os.path.join(output_dir, '00_FINAL_SUMMARY.md')}")
    
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
    results = await crawl_multiple_webpages_to_markdown(jyxx_urls, batch_size=50)
    
    return results

# 使用示例
if __name__ == "__main__":
    # 异步运行
    results = asyncio.run(main())
    
    # 或者直接调用批量爬取函数
    # your_url_list = [...]  # 你的URL列表
    # results = crawl_multiple_webpages_sync(your_url_list, batch_size=50)
