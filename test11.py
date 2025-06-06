import json
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
        start_index: 起始索引 (当前批次在总URL列表中的起始索引)
    """
    batch_dir = os.path.join(output_dir, f"batch_{batch_num:03d}")
    os.makedirs(batch_dir, exist_ok=True)
    
    batch_content = ""
    successful_count = 0
    
    for i, result in enumerate(results):
        # 文件的全局索引是批次起始索引 + 批次内索引 + 1
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
            # 这里的索引也是批次内的相对索引
            status = "✅ 成功" if result['success'] else "❌ 失败"
            error_msg = f" - {result.get('error', '')}" if not result['success'] else ""
            f.write(f"{start_index + i + 1}. {status} | {result.get('source', 'Unknown')} | {result.get('name', 'Unknown')}{error_msg}\n")
        
        f.write(f"\n---\n\n{batch_content}")
    
    print(f"💾 批次 {batch_num} 结果已保存到 {batch_dir}")
    return successful_count

def save_progress_log(output_dir, processed_count, total_count, successful_count, failed_count, start_time=None, end_time=None, output_dir_name=None):
    """
    保存进度日志
    Args:
        output_dir: 结果输出目录的完整路径
        processed_count: 截至目前已处理的URL总数
        total_count: 总URL数量
        successful_count: 截至目前成功的URL总数
        failed_count: 截至目前失败的URL总数
        start_time: 爬取任务开始时间
        end_time: 爬取任务结束时间 (如果已完成)
        output_dir_name: 结果输出目录的名称 (例如: crawl_results_20240101_120000)
    """
    progress_file = os.path.join(output_dir, "progress_log.json")
    
    existing_data = {}
    if os.path.exists(progress_file):
        try:
            with open(progress_file, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
        except Exception:
            pass # Ignore error if file is corrupted or unreadable
    
    progress_data = {
        "start_time": start_time or existing_data.get("start_time"),
        "end_time": end_time,
        "last_update": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "processed_count": processed_count,
        "total_count": total_count,
        "successful_count": successful_count,
        "failed_count": failed_count,
        "progress_percentage": round((processed_count / total_count) * 100, 2) if total_count > 0 else 0,
        "is_completed": processed_count >= total_count,
        "output_dir_name": output_dir_name or existing_data.get("output_dir_name")
    }
    
    if progress_data["start_time"] and progress_data["end_time"]:
        try:
            start_dt = datetime.strptime(progress_data["start_time"], '%Y-%m-%d %H:%M:%S')
            end_dt = datetime.strptime(progress_data["end_time"], '%Y-%m-%d %H:%M:%S')
            duration = end_dt - start_dt
            progress_data["total_duration_seconds"] = int(duration.total_seconds())
            progress_data["total_duration_formatted"] = str(duration).split('.')[0]
        except ValueError:
            pass # Date parsing error
    
    with open(progress_file, "w", encoding="utf-8") as f:
        json.dump(progress_data, f, ensure_ascii=False, indent=2)

def load_progress_log(output_dir_prefix="crawl_results_"):
    """
    加载最新的进度日志。
    查找最近创建的且未完成的爬取目录及其进度日志。
    """
    existing_dirs = [d for d in os.listdir('.') if os.path.isdir(d) and d.startswith(output_dir_prefix)]
    if not existing_dirs:
        return None, None

    # Sort directories by name (which includes timestamp), newest last
    existing_dirs.sort()
    
    # Iterate from newest to oldest to find an incomplete log
    for latest_output_dir in reversed(existing_dirs):
        progress_file = os.path.join(latest_output_dir, "progress_log.json")
        
        if os.path.exists(progress_file):
            try:
                with open(progress_file, "r", encoding="utf-8") as f:
                    progress_data = json.load(f)
                    if not progress_data.get("is_completed", True): # Only load if not completed
                        print(f"📊 找到未完成的进度日志: {progress_file}")
                        return progress_data, latest_output_dir
                    else:
                        print(f"✅ 进度日志已完成或无效，检查下一个。")
            except Exception as e:
                print(f"❌ 加载进度日志失败 ({progress_file}): {e}，检查下一个。")
    
    print(f"✅ 未找到任何未完成的进度日志，将开始新的爬取。")
    return None, None


def update_overall_summary(output_dir, all_results, total_successful, total_failed, current_batch, total_batches, batch_size, start_time, total_urls_overall):
    """
    更新总体汇总报告 (00_OVERALL_SUMMARY.md) - 实时进度报告
    """
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    processed_count = len(all_results) # This now includes dummy data for resumed runs
    total_urls = total_urls_overall # Use the explicitly passed total URL count
    
    duration_info = ""
    is_completed = processed_count >= total_urls # Check if all URLs are processed based on the actual total_urls
    
    progress_file = os.path.join(output_dir, "progress_log.json")
    if os.path.exists(progress_file):
        try:
            with open(progress_file, "r", encoding="utf-8") as f:
                progress_data = json.load(f)
                if progress_data.get("total_duration_formatted"):
                    duration_info = f"**总耗时**: {progress_data['total_duration_formatted']}  \n"
                elif progress_data.get("start_time"):
                    try:
                        start_dt = datetime.strptime(progress_data["start_time"], '%Y-%m-%d %H:%M:%S')
                        current_dt = datetime.now()
                        current_duration = current_dt - start_dt
                        duration_info = f"**当前耗时**: {str(current_duration).split('.')[0]}  \n"
                    except ValueError:
                        pass
        except Exception:
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
        
        for batch_num_iter in range(1, total_batches + 1):
            start_idx = (batch_num_iter - 1) * batch_size
            end_idx = min(start_idx + batch_size, total_urls)
            
            if batch_num_iter <= current_batch:
                # 已完成的批次
                # Note: `all_results` contains dummy results for previous batches on resume.
                # To get actual success/fail for previous batches, one might need to read `batch_XXX_summary.md`.
                # For this implementation, we rely on total_successful/total_failed and assume previous batches were successful
                # based on `progress_log.json`'s `processed_count`.
                f.write(f"- ✅ 批次 {batch_num_iter} (URL {start_idx + 1}-{end_idx}) - 已完成 - `batch_{batch_num_iter:03d}/`\n")
            elif batch_num_iter == current_batch + 1:
                # 正在处理的批次
                f.write(f"- 🔄 批次 {batch_num_iter} (URL {start_idx + 1}-{end_idx}) - 处理中...\n")
            else:
                # 待处理的批次
                f.write(f"- ⏳ 批次 {batch_num_iter} (URL {start_idx + 1}-{end_idx}) - 等待处理\n")
        
        # Display failed URLs only for the current run's failures, or all if we rebuild full all_results
        # For this batch-level resume, we show failures from the *current* run's `all_results`.
        # If `all_results` is only populated with dummy data for previous runs,
        # then this section will only show failures from the current execution segment.
        failed_results_current_run = [r for r in all_results[processed_count - (processed_count - (total_successful + total_failed)):] if not r.get('success', False)] # Slice to get only current run's results
        
        if failed_results_current_run:
            f.write(f"\n## 🔍 失败URL详情 (共{len(failed_results_current_run)}个 - 当前运行批次)\n\n")
            for i, result in enumerate(failed_results_current_run, 1):
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


def generate_final_summary_report(output_dir, all_results, total_successful, total_failed, url_list_original, batch_size, start_time, current_end_time, total_urls_overall):
    """
    生成或更新最终汇总报告 (00_FINAL_SUMMARY.md)
    这个报告会随着每批次处理完成而更新，反映当前的累计结果。
    """
    total_urls = total_urls_overall # Use the explicitly passed total URL count
    processed_urls_count = len(all_results) # This now includes dummy data for resumed runs
    total_batches = (total_urls + batch_size - 1) // batch_size

    final_summary_file = os.path.join(output_dir, "00_FINAL_SUMMARY.md")

    progress_file = os.path.join(output_dir, "progress_log.json")
    duration_info = ""
    is_completed = processed_urls_count >= total_urls 
    
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
                    except ValueError:
                        pass
        except Exception:
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
        
        # Group results by batch for accurate statistics from all_results
        batch_wise_results = {}
        for result in all_results:
            batch_num = result.get('batch_num')
            if batch_num not in batch_wise_results:
                batch_wise_results[batch_num] = []
            batch_wise_results[batch_num].append(result)

        for batch_num in sorted(batch_wise_results.keys()):
            batch_results = batch_wise_results[batch_num]
            # Use sum(1 for r in batch_results if r.get('success', False)) if using dummy data
            # If using actual data (if rebuilt from files), then check 'success'
            batch_success = sum(1 for r in batch_results if r.get('success', False))
            batch_fail = len(batch_results) - batch_success
            
            start_idx_original = (batch_num - 1) * batch_size
            end_idx_original = min(start_idx_original + batch_size, total_urls)

            f.write(f"### 批次 {batch_num} (URL {start_idx_original + 1}-{end_idx_original})\n")
            f.write(f"- ✅ 成功: {batch_success}\n")
            f.write(f"- ❌ 失败: {batch_fail}\n")
            f.write(f"- 📁 目录: `batch_{batch_num:03d}/`\n\n")
        
        f.write("## 📋 所有URL详细内容 (累计)\n\n") 
        
        cumulative_content_for_final_report = ""
        for i, result in enumerate(all_results, 1):
            # If `all_results` contains dummy entries for previous runs,
            # this part will only show full content for the current run's processed items.
            # For previously processed (resumed) items, it will only show success/fail status
            # unless a more complex `all_results` reconstruction from files is implemented.
            if result.get('success', False) and 'content' in result: # Only show content if available
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
                # For failed or dummy items, include their details and error, but no content
                status_text = "成功 (旧批次)" if result.get('success', False) else "失败"
                cumulative_content_for_final_report += f"""# {status_text}: {result.get('name', 'Unknown URL')}

**来源**: {result.get('source', 'Unknown')}  
**URL**: {result.get('url', 'N/A')}  
**错误**: {result.get('error', 'N/A')}  
**爬取时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---
"""
            
            if i < len(all_results):
                cumulative_content_for_final_report += f"\n\n{'='*80}\n\n"

        f.write(cumulative_content_for_final_report)


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
    每处理指定数量的URL后进行一次文件保存操作，并支持以批次为单位的断点续传。
    
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
    
    all_results = [] # Accumulates results (can include dummy entries for resumed items)
    total_successful = 0
    total_failed = 0
    
    start_index_for_crawl = 0 # This will be the starting point for the current crawl session
    output_dir = ""
    start_time = ""

    total_urls_to_process = len(url_list) # Total URLs from the input list
    total_batches = (total_urls_to_process + batch_size - 1) // batch_size
    

    # 尝试加载进度日志
    progress_data, existing_output_dir = load_progress_log()

    if progress_data and existing_output_dir:
        start_index_for_crawl = progress_data.get("processed_count", 0)
        output_dir = existing_output_dir
        start_time = progress_data.get("start_time", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        total_successful = progress_data.get("successful_count", 0)
        total_failed = progress_data.get("failed_count", 0)

        # Populate all_results with dummy entries for already processed URLs
        # This is crucial for accurate 'processed_count' in summary reports
        for i in range(start_index_for_crawl):
            # Create a placeholder for already processed URLs.
            # We don't need their actual content here, just a 'success' status
            # to keep counts accurate for the summary reports.
            # We assume URLs up to start_index_for_crawl were counted in successful/failed_count
            # from the loaded progress_data.
            # Add basic info to ensure name/url are available for reports, even if dummy
            dummy_item = url_list[i] if i < len(url_list) else {}
            all_results.append({
                'success': True, # Assume success for already processed for general counts
                'batch_num': (i // batch_size) + 1,
                'name': dummy_item.get('name', f"Dummy URL {i+1}"),
                'url': dummy_item.get('final_url', f"dummy_url_{i+1}"),
                'source': dummy_item.get('source', 'Previous Run'),
                'error': None, # No error for dummy success
                'title': 'Previously Processed'
            })


        print(f"✅ 从断点续传，将从第 {start_index_for_crawl + 1} 个URL开始处理。")
        print(f"   已成功: {total_successful}, 已失败: {total_failed}")
    else:
        # 创建新的输出目录
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = f"crawl_results_{timestamp}"
        start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        os.makedirs(output_dir, exist_ok=True)
        # 初始化进度日志，记录开始时间
        save_progress_log(output_dir, 0, total_urls_to_process, 0, 0, start_time=start_time, output_dir_name=output_dir)
        print(f"🆕 未找到有效进度，将开始新的爬取并创建目录: {output_dir}")
    
    
    # 调整起始批次号
    current_batch_start_index = start_index_for_crawl // batch_size
    
    for batch_num_idx in range(current_batch_start_index, total_batches):
        start_index = batch_num_idx * batch_size # Start index of the current *full* batch in url_list
        end_index = min(start_index + batch_size, total_urls_to_process)
        current_batch_urls = url_list[start_index:end_index] # URLs for the *entire* current batch
        
        print(f"\n{'='*80}")
        print(f"🔄 处理批次 {batch_num_idx + 1}/{total_batches}")
        print(f"📋 URL范围: {start_index + 1} - {end_index}")
        print(f"📊 当前批次大小: {len(current_batch_urls)}") 
        print(f"{'='*80}")
        
        batch_results_current_run = [] # Collect results only for this batch in the current run
        
        # Process every URL in the current batch (even if partially done before)
        for i, item in enumerate(current_batch_urls):
            global_index = start_index + i + 1 # Correct global index for display and tracking within this batch

            print(f"\n{'.'*60}")
            print(f"处理第 {global_index}/{total_urls_to_process} 个URL (批次内第 {i+1}/{len(current_batch_urls)} 个)")
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
                    'batch_num': batch_num_idx + 1 
                }
                batch_results_current_run.append(result)
                total_failed += 1
                continue
            
            # 爬取单个网页
            result = await crawl_single_webpage_to_markdown(
                item['final_url'],
                f"{item.get('source', 'Unknown')} - {item.get('name', 'Unknown')}"
            )
            
            # 添加额外信息
            result['name'] = item.get('name', 'Unknown')
            result['batch_num'] = batch_num_idx + 1 
            batch_results_current_run.append(result)
            
            if result['success']:
                total_successful += 1
            else:
                total_failed += 1
            
            # 添加延迟以避免过于频繁的请求
            await asyncio.sleep(1)
        
        # After processing all URLs in the current batch:
        # Save current batch's results (always use start_index for batch file naming)
        batch_successful_count = save_batch_results(batch_results_current_run, output_dir, batch_num_idx + 1, start_index)
        
        # Extend all_results with the current batch's results
        all_results.extend(batch_results_current_run) 

        # Update progress log - END OF BATCH update
        processed_count_after_batch = len(all_results)
        is_final_batch = (batch_num_idx == total_batches - 1)
        current_end_time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        save_progress_log(output_dir, processed_count_after_batch, total_urls_to_process, total_successful, total_failed, end_time=current_end_time_str if is_final_batch else None, output_dir_name=output_dir)
        
        # Update overall summary (real-time progress report)
        update_overall_summary(output_dir, all_results, total_successful, total_failed, batch_num_idx + 1, total_batches, batch_size, start_time, total_urls_to_process)

        # Update final summary report (cumulative report) after each batch
        generate_final_summary_report(output_dir, all_results, total_successful, total_failed, url_list, batch_size, start_time, current_end_time_str, total_urls_to_process)
        
        print(f"\n📊 批次 {batch_num_idx + 1} 完成统计:")
        print(f"✅ 批次成功: {batch_successful_count}")
        print(f"❌ 批次失败: {len(batch_results_current_run) - batch_successful_count}")
        print(f"📈 总体进度: {processed_count_after_batch}/{total_urls_to_process} ({(processed_count_after_batch/total_urls_to_process*100):.1f}%)")
        print(f"📊 累计成功: {total_successful}")
        print(f"📊 累计失败: {total_failed}")
        
        # Pause between batches
        if batch_num_idx < total_batches - 1:
            print("⏸️  批次间暂停 3 秒...")
            await asyncio.sleep(3)
    
    # Final updates after all batches are done
    final_end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    save_progress_log(output_dir, total_urls_to_process, total_urls_to_process, total_successful, total_failed, end_time=final_end_time, output_dir_name=output_dir)
    update_overall_summary(output_dir, all_results, total_successful, total_failed, total_batches, total_batches, batch_size, start_time, total_urls_to_process)
    generate_final_summary_report(output_dir, all_results, total_successful, total_failed, url_list, batch_size, start_time, final_end_time, total_urls_to_process)

    print(f"\n🎉 批量爬取全部完成！")
    print(f"📊 最终统计:")
    print(f"   总数量: {total_urls_to_process}")
    print(f"   ✅ 成功: {total_successful}")
    print(f"   ❌ 失败: {total_failed}")
    print(f"   📈 成功率: {(total_successful/total_urls_to_process*100):.2f}%")
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
