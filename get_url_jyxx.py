# 通过模拟点击获取所有新标签页的最终重定向URL，支持翻页操作，并保存到JSON文件
from playwright.sync_api import sync_playwright
import json
import os
import time
from datetime import datetime

def get_final_redirect_url(page, initial_url, wait_time=5):
    """
    获取单个URL的最终重定向URL
    
    Args:
        page: Playwright页面对象
        initial_url: 初始URL
        wait_time: 等待重定向的时间（秒）
    
    Returns:
        包含重定向信息的字典
    """
    redirect_chain = [initial_url]
    current_url = initial_url
    
    try:
        # 访问初始URL
        page.goto(initial_url, wait_until='domcontentloaded')
        current_url = page.url
        
        if current_url != initial_url:
            redirect_chain.append(current_url)
        
        # 等待可能的JavaScript重定向，分段检查
        for i in range(wait_time * 2):  # 每0.5秒检查一次
            time.sleep(0.5)
            new_url = page.url
            
            if new_url != current_url:
                print(f"    检测到重定向: {current_url} -> {new_url}")
                redirect_chain.append(new_url)
                current_url = new_url
        
        # 最终等待确保页面完全加载
        try:
            page.wait_for_load_state('networkidle', timeout=3000)
        except:
            pass  # 忽略超时
        
        final_url = page.url
        if final_url != current_url:
            redirect_chain.append(final_url)
        
        # 获取页面标题
        try:
            page_title = page.title()
        except:
            page_title = "无法获取标题"
        
        return {
            'success': True,
            'initial_url': initial_url,
            'final_url': final_url,
            'redirect_chain': redirect_chain,
            'total_redirects': len(redirect_chain) - 1,
            'page_title': page_title
        }
    
    except Exception as e:
        return {
            'success': False,
            'initial_url': initial_url,
            'final_url': initial_url,
            'error': str(e),
            'redirect_chain': redirect_chain,
            'total_redirects': 0,
            'page_title': '获取失败'
        }

def get_all_popup_urls_with_redirect(target_url,  max_pages,  link_selector=".class-item"):
    """
    获取所有匹配元素点击后打开的新标签页URL，并跟踪重定向到最终URL
    
    Args:
        target_url: 目标网页URL
        link_selector: 链接选择器，默认为.class-item
        max_pages: 最大处理页数，翻多少页
    
    Returns:
        包含所有URL信息的列表
    """
    with sync_playwright() as p:
        # 设置更真实的浏览器指纹
        browser = p.chromium.launch(
            headless=False,  # 可以改为True进行无头模式
            args=[
                "--disable-blink-features=AutomationControlled",
                "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ]
        )
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            locale="zh-CN"
        )
        
        # 创建主页面
        main_page = context.new_page()
        # 创建用于重定向跟踪的页面
        redirect_page = context.new_page()
        
        try:
            # 访问目标网页
            main_page.goto(target_url, wait_until="domcontentloaded")
            main_page.wait_for_load_state("networkidle", timeout=8000)
            main_page.wait_for_selector(".info-item", state="attached", timeout=8000)
            main_page.wait_for_timeout(1000)

            all_urls = []  # 存储所有页面的URL信息
            
            # 循环处理每一页
            for page_num in range(max_pages):
                print(f"\n=== 正在处理第 {page_num + 1} 页 ===")
                
                # 等待页面加载完成
                main_page.wait_for_selector(".info-item", state="attached", timeout=8000)
                main_page.wait_for_timeout(1000)
                
                # 获取当前页面所有匹配的元素
                elements = main_page.query_selector_all('[class="info-item"]')
                print(f"第 {page_num + 1} 页找到 {len(elements)} 个匹配的元素")
                
                # 处理当前页面的每个元素
                for i, element in enumerate(elements):
                    element_info = {
                        # 'page_number': page_num + 1,
                        # 'element_index': i + 1,
                        'source': f'第 {page_num + 1} 页第 {i+1} 个元素',
                        'name': '未知',
                        # 'initial_url': '获取失败',
                        'final_url': '获取失败',
                        # 'redirect_info': {}
                    }
                    
                    try:
                        print(f"  正在处理第 {page_num + 1} 页的第 {i+1} 个元素...")
                        
                        # 获取标题
                        title_element = element.query_selector('a')
                        if title_element:
                            title = title_element.get_attribute('title') or title_element.inner_text().strip()
                            element_info['name'] = title
                            print(f"    标题: {title}")
                        
                        # 监听新页面打开事件
                        with main_page.expect_popup() as new_page_info:
                            element.click()
                        
                        # 获取新页面和初始URL
                        new_page = new_page_info.value
                        initial_url = new_page.url
                        # element_info['initial_url'] = initial_url
                        
                        print(f"    初始URL: {initial_url}")
                        
                        # 关闭弹出的页面，我们用专门的页面来跟踪重定向
                        new_page.close()
                        
                        # 使用专门的页面跟踪重定向
                        print(f"    开始跟踪重定向...")
                        redirect_info = get_final_redirect_url(redirect_page, initial_url, wait_time=3)
                        
                        element_info['final_url'] = redirect_info['final_url']
                        # element_info['redirect_info'] = redirect_info
                        
                        if redirect_info['success']:
                            print(f"    ✅ 最终URL: {redirect_info['final_url']}")
                            if redirect_info['total_redirects'] > 0:
                                print(f"    🔄 经过 {redirect_info['total_redirects']} 次重定向")
                            print(f"    📄 页面标题: {redirect_info['page_title']}")
                        else:
                            print(f"    ❌ 重定向跟踪失败: {redirect_info.get('error', '未知错误')}")
                        
                        # 等待一小段时间，避免操作过快
                        main_page.wait_for_timeout(1000)
                        
                    except Exception as e:
                        print(f"    ❌ 处理第 {page_num + 1} 页第 {i+1} 个元素时出错: {e}")
                        # element_info['redirect_info'] = {
                        #     'success': False,
                        #     'error': str(e)
                        # }
                    
                    all_urls.append(element_info)
                
                print(f"第 {page_num + 1} 页处理完成")
                
                # 如果不是最后一页，点击下一页按钮
                if page_num < max_pages - 1:
                    try:
                        print(f"  正在点击第 {page_num + 1} 次下一页按钮...")
                        
                        # 检查下一页按钮是否存在且可点击
                        next_button = main_page.query_selector('a.next')
                        if next_button:
                            # 检查按钮是否被禁用
                            is_disabled = next_button.get_attribute('class')
                            if 'disabled' not in (is_disabled or ''):
                                # 滚动到按钮位置，确保可见
                                next_button.scroll_into_view_if_needed()
                                main_page.wait_for_timeout(500)
                                
                                # 点击下一页按钮
                                next_button.click()
                                
                                # 等待页面加载
                                main_page.wait_for_load_state("networkidle", timeout=8000)
                                main_page.wait_for_timeout(2000)
                                
                                print(f"  ✅ 成功点击下一页，即将处理第 {page_num + 2} 页")
                            else:
                                print("  ⚠️ 下一页按钮已禁用，可能已到达最后一页")
                                break
                        else:
                            print("  ⚠️ 未找到下一页按钮，可能已到达最后一页")
                            break
                            
                    except Exception as e:
                        print(f"  ❌ 点击下一页按钮时出错: {e}")
                        break
            
            return all_urls
            
        except Exception as e:
            print(f"❌ 获取URL时出错: {e}")
            return []
        finally:
            print(f"🔚 获取URL完成, 关闭浏览器")
            browser.close()

def save_urls_to_json(urls, filename="jyxx_final_urls.json"):
    """
    将URL数据保存到JSON文件
    
    Args:
        urls: URL列表
        filename: 输出文件名
    """
    try:
        # 统计数据
        total_count = len(urls)
        success_count = len([url for url in urls if url.get('final_url') != '获取失败'])
        failed_count = total_count - success_count
        # redirect_count = len([url for url in urls if url.get('redirect_info', {}).get('total_redirects', 0) > 0])
        
        # 准备要保存的数据
        data = {
            "metadata": {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total_count": total_count,
                "success_count": success_count,
                "failed_count": failed_count,
                # "redirect_count": redirect_count,
                "description": "获取重定向后的最终URL数据"
            },
            "statistics": {
                "success_rate": f"{(success_count/total_count*100):.1f}%" if total_count > 0 else "0%",
                # "redirect_rate": f"{(redirect_count/success_count*100):.1f}%" if success_count > 0 else "0%"
            },
            "urls": urls
        }
        
        # 保存到JSON文件
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"\n=== 📄 数据已保存到 {filename} ===")
        print(f"📅 保存时间: {data['metadata']['timestamp']}")
        print(f"📊 总数量: {data['metadata']['total_count']}")
        print(f"✅ 成功数量: {data['metadata']['success_count']}")
        print(f"❌ 失败数量: {data['metadata']['failed_count']}")
        # print(f"🔄 有重定向: {data['metadata']['redirect_count']}")
        print(f"📈 成功率: {data['statistics']['success_rate']}")
        # print(f"🔄 重定向率: {data['statistics']['redirect_rate']}")
        
        return True
        
    except Exception as e:
        print(f"❌ 保存JSON文件时出错: {e}")
        return False

def print_summary(urls):
    """
    打印处理结果摘要
    """
    print("\n" + "="*80)
    print("📋 处理结果摘要")
    print("="*80)
    
    for i, url_info in enumerate(urls):
        status = "✅" if url_info.get('final_url') != '获取失败' else "❌"
        # redirects = url_info.get('redirect_info', {}).get('total_redirects', 0)
        # redirect_text = f" (🔄{redirects}次重定向)" if redirects > 0 else ""
        
        print(f"{status} {url_info['source']}: {url_info['name']}")
        print(f"   📍 最终URL: {url_info['final_url']}")
        
        # if not url_info.get('redirect_info', {}).get('success', False):
        #     error = url_info.get('redirect_info', {}).get('error', '未知错误')
        #     print(f"   ⚠️  错误: {error}")
        
        print()

# 使用示例
if __name__ == "__main__":
    target_url = "https://www.cqggzy.com/jyxx/transaction_detail.html"
    # max_pages: 最大处理页数，翻多少页
    max_pages = 10
    print("🚀 开始获取URLs并跟踪重定向...")
    print(f"🎯 目标URL: {target_url}")
    print(f"📄 将处理前{max_pages}页数据")
    print("-" * 80)
    
    # 获取所有URL及其重定向信息
    urls = get_all_popup_urls_with_redirect(target_url, max_pages)
    
    if urls:
        # 打印摘要
        print_summary(urls)
        
        # 保存到JSON文件
        save_success = save_urls_to_json(urls, "jyxx_final_urls.json")
        if save_success:
            print("🎉 数据已成功保存到 jyxx_final_urls.json")
        else:
            print("💥 保存数据失败")
    else:
        print("💥 没有获取到任何URL数据")
    
    print("\n🏁 程序执行完成！")