crwl https://www.nbcnews.com/business -o markdown
crwl https://www.cqggzy.com/jyjg/transaction_detail.html -o markdown

https://www.cqggzy.com/jyjg/transaction_detail.html


import asyncio
from crawl4ai import *

async def main():
    
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            # url="https://www.cqggzy.com/",
            # url="https://news.cqjjnet.com/html/col95569.htm",            
            # url="https://www.cqggzy.com/tzgg/second-page-zytz.html",            
            url="https://www.cqggzy.com/jyjg/transaction_detail.html",            
        )
        with open("result01.md", "w", encoding="utf-8") as f:
            f.write(result.markdown)

if __name__ == "__main__":
    asyncio.run(main())


#showList
<a href="javascript:void(0);" class="label-item" value="014010">
						中介超市
					</a>
                    
使用 Crawl4AI 提取 JavaScript onclick 事件中的动态 URL1. 引言：动态网页抓取的挑战随着现代网络技术的发展，网页内容和用户交互变得日益复杂。传统的网页抓取工具主要依赖于解析静态 HTML，但这种方法在面对大量由 JavaScript 动态渲染或控制内容的网站时，往往力不从心 1。网页抓取已从简单的 HTML 解析演变为需要处理复杂的 JavaScript 渲染内容。用户提出的问题，即网页代码中包含 <a id="link1" onclick="openurl('page1')">Go to Page 1</a> 时如何获取实际的抓取 URL，恰恰揭示了这一核心挑战。在这种情况下，链接的实际目标并非直接存在于 href 属性中，而是通过 onclick 属性中调用的 JavaScript 函数 openurl('page1') 来动态确定的。这意味着，一个仅抓取原始 HTML 的工具将无法识别或追踪这种导航行为。因此，为了有效应对此类现代网页挑战，需要一个能够模拟真实浏览器环境、执行 JavaScript 并与动态内容进行交互的工具。Crawl4AI 正是为此而设计的一款开源 Python 库 1。它专注于克服传统抓取工具的局限性，特别擅长处理 JavaScript 密集型网站。Crawl4AI 的核心能力在于其能够渲染页面，从而确保即使是动态加载的内容也能被捕获 1。此外，它还能够生成 AI 就绪的数据，这表明其在处理复杂网页结构方面具有强大的能力，能够将混乱的网页转换为清晰的 JSON 或 Markdown 格式 1。这种需求反映了网页抓取范式的根本性转变。用户查询中隐含的 onclick 属性与 JavaScript 函数调用 (openurl('page1')) 明确指出，客户端 JavaScript 正在主导导航行为。这意味着传统的基于 requests 和 BeautifulSoup 的方法，由于仅获取原始 HTML，将无法感知此类动态行为。因此，一个有效的工具必须能够执行 JavaScript 并模拟浏览器环境。Crawl4AI 的设计，特别是其利用 Playwright 等无头浏览器（headless browser）的能力，直接解决了这一范式转变 1。它不仅仅是获取 HTML，更是像用户一样“体验”网页，包括所有的 JavaScript 交互。这表明，现代有效的网页抓取正日益演变为浏览器自动化。2. 理解 JavaScript 驱动的重定向机制在动态网页环境中，onclick 属性扮演着至关重要的角色。它是一个 HTML 事件属性，当用户点击某个元素时，会触发一个指定的 JavaScript 函数执行 5。在用户提供的示例中，onclick="openurl('page1')" 表示当带有 id="link1" 的 <a> 标签被点击时，名为 openurl 的 JavaScript 函数将被调用，并传入参数 "page1"。JavaScript 提供了多种方法来实现页面重定向或打开新页面，这些方法通常在 onclick 事件中被调用：
window.location.href: 这是最常见的重定向方式之一。通过将 window.location.href 属性设置为新的 URL，浏览器会加载并导航到该 URL 6。这种方法会将新页面添加到浏览器的历史记录中，用户可以通过“后退”按钮返回到前一个页面。例如：window.location.href = 'https://www.example.com'; 6。
location.replace(): 类似于 window.location.href，但 location.replace() 方法会用新的 URL 替换当前页面在浏览器历史记录中的条目 6。这意味着用户无法通过浏览器的“后退”按钮返回到被替换的页面。例如：location.replace('https://www.example.com'); 6。
window.open(): 此方法用于在一个新的浏览上下文（通常是新标签页或新窗口）中打开指定的 URL 8。例如：window.open('http://www.google.com'); 9。它提供了更多的参数来控制新窗口的特性。
javascript:void(0): 这种表达式通常与 onclick 属性结合使用，放置在 <a> 标签的 href 属性中 5。它的作用是防止链接的默认行为（即导航到 # 或重新加载页面），从而确保点击事件完全由 onclick 中定义的 JavaScript 函数处理 5。这与用户查询中的场景高度相关，因为实际的导航目标完全由 onclick 中的 JavaScript 决定，而 href 属性可能为空或设置为 javascript:void(0)。
这些 JavaScript 驱动的重定向机制揭示了动态 URL 的潜在性质。在直接的 HTML 代码（例如 <a id="link1" onclick="openurl('page1')">）中，目标 URL 并没有立即显现。该 URL 隐藏在 openurl JavaScript 函数内部，而这个函数可能在页面的任何位置定义（内联脚本或外部 JS 文件）。这意味着抓取工具不仅需要执行 JavaScript，还可能需要理解或监控其效果，以确定实际的导航目标。这进一步强调了对完整浏览器环境的需求，该环境能够解释和运行页面的整个 JavaScript 上下文，而不仅仅是解析静态属性。此外，window.location.href 和 location.replace() 之间的选择对浏览器历史记录具有影响 6。虽然这对于抓取可能看似微不足道，但它会影响抓取工具如何模拟用户行为，或者在多步骤流程中是否能够“返回”。window.open() 则引入了新标签页/窗口的复杂性，如果 openurl 函数使用它，Crawl4AI 将需要管理这些新的上下文。这表明，理解具体的 JavaScript 重定向方法可以为更复杂的抓取策略提供信息，例如会话管理 10。下表总结了这些常见的 JavaScript 重定向方法：表 1：常见 JavaScript 重定向方法比较
方法描述对浏览器历史记录的影响是否在新标签页/窗口打开典型 HTML 用法与 onclick 抓取的相关性window.location.href设置当前窗口的完整 URL，导致导航。添加新条目，可通过“后退”按钮返回否onclick="window.location.href='url'"常见于 onclick 事件中，用于直接导航。location.replace()用指定 URL 替换当前文档，并移除历史记录。替换当前条目，无法通过“后退”按钮返回否onclick="location.replace('url')"常见于 onclick 事件中，用于需要防止用户回退的导航。window.open()在新的浏览上下文（标签页或窗口）中加载资源。在新上下文中有自己的历史记录是onclick="window.open('url')"常见于 onclick 事件中，用于打开外部链接或弹出窗口。javascript:void(0)评估为 undefined，不执行任何操作。无直接影响，通常与 onclick 结合否<a href="javascript:void(0)" onclick="func()">用于 href 属性以防止默认链接行为，确保 onclick 中的 JavaScript 完全控制导航。对于本查询场景至关重要 5。
3. Crawl4AI 处理动态内容和 JavaScript 执行的能力Crawl4AI 的核心优势在于其处理动态网页内容和执行 JavaScript 的强大能力。
完整的浏览器渲染：Crawl4AI 基于 Playwright 构建，Playwright 是一个强大的浏览器自动化引擎，能够启动无头浏览器实例（如 Chromium、Firefox 和 WebKit）2。这至关重要，因为这意味着 Crawl4AI 不仅仅是获取原始 HTML；它会像真实的浏览器一样渲染页面，执行所有相关的 JavaScript，并构建文档对象模型（DOM）1。这种能力对于与动态加载或其行为由 JavaScript 控制的元素进行交互至关重要 1。
执行自定义 JavaScript (js_code)：Crawl4AI 提供了 CrawlerRunConfig 中的 js_code 参数，可以直接在页面上下文中注入和执行任意 JavaScript 片段 2。这允许模拟用户交互，例如点击、表单提交、滚动或触发特定的 JavaScript 函数 2。为了启用 JavaScript 执行，BrowserConfig 中的 java_script_enabled 必须设置为 True 3。
异步核心以实现高性能：Crawl4AI 基于 Python 的 asyncio 框架构建，支持高吞吐量和非阻塞 I/O 操作，这对于高效地大规模抓取动态网站至关重要 2。
Crawl4AI 利用 Playwright 并允许 js_code 注入，这标志着从被动数据获取到主动用户行为模拟的转变。对于 onclick 事件，Crawl4AI 不仅仅是猜测 URL；它扮演着浏览器的角色，执行 JavaScript 并观察由此产生的导航。这种主动模拟使其能够有效处理动态内容，因为它复制了人类用户将触发的精确事件序列。这是与更简单抓取工具的关键区别。此外，虽然 js_code 可以触发 onclick 事件，但动态内容通常涉及网络请求和渲染延迟。简单地执行点击并立即尝试获取 URL 可能会导致在导航完成或新内容完全加载之前就获取了 URL。Crawl4AI 通过 wait_for 条件解决了这个问题 2。这可以是等待特定 CSS 选择器出现 (wait_for_selector) 或 JavaScript 函数返回 true (wait_for_function)。这强调了成功的动态抓取不仅仅是触发操作，还在于与页面的动态行为同步，以确保在正确状态下捕获数据。这是动态抓取中一个常见的陷阱，Crawl4AI 明确有助于缓解。4. 使用 Crawl4AI 模拟点击并获取实际 URL要使用 Crawl4AI 模拟点击并获取 JavaScript 驱动的导航后的实际 URL，主要涉及 AsyncWebCrawler 类及其 arun() 方法。

AsyncWebCrawler 和 arun() 方法：

AsyncWebCrawler 是 Crawl4AI 中用于启动抓取的核心类 12。
arun(url, config=None) 方法用于抓取单个 URL 12。



模拟点击的步骤：

初始化 AsyncWebCrawler：创建一个 AsyncWebCrawler 实例。在此过程中，应可选地传入一个 BrowserConfig 对象，以确保 JavaScript 被启用并设置无头模式（如果需要）。
定义用于点击的 JavaScript：构造一个 JavaScript 字符串，该字符串能够选择目标元素（例如，使用 document.getElementById('link1') 或 document.querySelector('#link1')），并通过调用 .click() 方法模拟点击 2。例如：const link = document.getElementById('link1'); if (link) { link.click(); }
配置 CrawlerRunConfig：将上述 JavaScript 字符串（或字符串列表）传递给 CrawlerRunConfig 的 js_code 参数。
实现等待条件：至关重要的是，在 js_code 执行后，抓取工具需要等待页面完成导航并加载新内容。这可以通过在 CrawlerRunConfig 中使用 wait_for 参数来实现，例如 wait_for_selector（等待特定 CSS 选择器出现）、wait_for_function（等待自定义 JavaScript 函数返回真值）或设置 page_timeout（页面加载超时时间）2。
执行抓取：调用 await crawler.arun(initial_url, config=run_conf)。



从 CrawlResult 中获取最终 URL：

arun() 方法会返回一个 CrawlResult 对象 12。
CrawlResult 对象包含一个 url 属性，该属性表示“抓取后的最终 URL（在任何重定向之后）”10。
这个 result.url 属性正是用户所需要的，因为 Crawl4AI 会自动追踪由 JavaScript 执行导致的 URL 变化。


这里最重要的一点是 Crawl4AI 如何抽象了 JavaScript 驱动的导航复杂性。它不需要用户解析 JavaScript、拦截网络请求或手动跟踪浏览器历史记录，Crawl4AI 的 CrawlResult.url 属性会自动提供最终解析的 URL 12。这种强大的抽象简化了抓取过程，使开发人员能够专注于数据提取，而不是复杂的浏览器事件处理。它展示了 Crawl4AI 对于 AI 就绪数据的价值主张，因为它提供了干净、交互后的页面状态。js_code 用于触发操作，而 wait_for 用于确保页面状态稳定 2，这种组合是动态抓取的基本模式。这不仅仅是执行脚本；它是在异步操作中管理浏览器状态。wait_for 确保 Crawl4AI 不会过早返回 CrawlResult，即在 onclick 操作完全生效（例如，导航完成且新内容加载）之前。这对于动态环境中的数据完整性和可靠性至关重要。5. 实际实现：Crawl4AI 逐步示例为了演示如何使用 Crawl4AI 模拟点击并获取动态 URL，以下是一个逐步的 Python 代码示例：前提条件
Python 3.8 或更高版本 1。
已安装 crawl4ai 库（例如，通过 pip install -U crawl4ai 和运行 crawl4ai-setup 来安装 Playwright 浏览器二进制文件）12。
代码示例Pythonimport asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

async def get_dynamic_url(initial_url: str):
    # 1. 配置浏览器：启用 JavaScript 并以无头模式运行
    # headless=True: 浏览器在后台运行，不显示图形界面。
    # java_script_enabled=True: 确保 JavaScript 执行被启用，这是处理 onclick 事件的关键。
    browser_conf = BrowserConfig(headless=True, java_script_enabled=True)

    # 2. 定义用于模拟点击的 JavaScript 代码
    # 这段代码会查找 id 为 "link1" 的 <a> 标签，并模拟点击它。
    # 如果 openurl('page1') 是全局定义的函数，也可以直接调用它。
    # 但通常，模拟元素点击更具鲁棒性，因为它会触发所有附加到该元素的事件监听器。
    js_click_code = """
    (async () => {
        const linkElement = document.getElementById('link1');
        if (linkElement) {
            linkElement.click();
            // 至关重要：点击后等待导航完成。
            // 这里的 setTimeout 只是一个简单的示例；
            // 对于更鲁棒的等待新内容加载或 URL 变化，应考虑使用 wait_for_selector 或 wait_for_function。
            await new Promise(resolve => setTimeout(resolve, 3000)); // 根据实际页面加载速度调整延迟时间
        }
    })();
    """

    # 3. 配置抓取运行：绕过缓存并执行 JavaScript
    run_conf = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS, # 确保每次都获取最新内容，避免使用缓存中的旧数据 [12, 17]
        js_code=[js_click_code],     # 传递要执行的 JavaScript 代码列表 [3, 13]
        # 替代方案：使用 wait_for 进行更具体的条件等待，例如：
        # wait_for="js:() => window.location.href.includes('page1')" # 等待 URL 包含 'page1'
        # wait_for="css:#new-page-content" # 等待新页面上的某个特定元素出现
        page_timeout=30000 # 整体页面加载或脚本执行的超时时间（毫秒）[11, 13]
    )

    # 4. 初始化并运行抓取器
    async with AsyncWebCrawler(config=browser_conf) as crawler:
        print(f"正在导航到初始 URL: {initial_url}")
        result = await crawler.arun(url=initial_url, config=run_conf)

        # 5. 从 CrawlResult 中检索最终 URL
        if result.success:
            final_url = result.url # 此属性包含 JavaScript 触发导航和任何后续重定向后的最终 URL [12, 16]
            print(f"抓取成功。最终 URL: {final_url}")
            print(f"页面 HTML 长度: {len(result.html)} 字节")
            # 还可以访问其他数据，例如 markdown、text 等。
            # print(result.markdown.fit_markdown[:500])
        else:
            print(f"抓取失败: {result.error_message}")
            if result.url:
                print(f"最后已知 URL: {result.url}")
            else:
                print("未获取到 URL。")

if __name__ == "__main__":
    # 替换为包含 <a id="link1" onclick="openurl('page1')"> 元素的实际目标 URL
    # 为了演示，可能需要一个本地 HTML 文件或测试服务器。
    # 例如：如果您的初始 HTML 在 http://localhost:8000/index.html
    # 并且 openurl('page1') 导航到 http://localhost:8000/page1.html
    target_initial_url = "http://localhost:8000/index.html"
    asyncio.run(get_dynamic_url(target_initial_url))
代码组件说明

BrowserConfig：此配置类用于设置浏览器环境。headless=True 使浏览器在没有可见用户界面的情况下运行，而 java_script_enabled=True 对于执行 onclick 函数至关重要 3。


js_click_code：这个字符串包含了 Crawl4AI 将注入并执行的 JavaScript 代码。document.getElementById('link1').click() 模拟了用户的点击行为。代码中包含的 await new Promise(resolve => setTimeout(resolve, 3000)); 是一个必要的等待占位符，它允许浏览器处理导航并加载新内容 2。
示例代码中的 setTimeout 是一个基本但有时必要的等待机制。虽然 Crawl4AI 提供了更高级的 wait_for 参数 2，但有时 JavaScript 本身需要等待内部进程（例如，AJAX 调用、DOM 操作）在导航真正开始或完成之前。setTimeout 在注入的 JS 中是一种处理这种情况的简单方法。更深入的理解会建议在 js_code 执行之后，或者在多步骤会话中，使用 Crawl4AI 更鲁棒的 wait_for 选项（如 wait_for_selector 或 wait_for_function），以确保页面在检查 result.url 之前达到所需的状态。这突出了理解目标网站特定动态行为的重要性。


CrawlerRunConfig：此配置类用于设置特定的抓取任务。cache_mode=CacheMode.BYPASS 确保获取最新数据。js_code 参数用于传递点击脚本。page_timeout 提供了一个安全网，防止无限等待 12。


result.url：在 arun() 方法完成后，CrawlResult 对象的此属性将提供 JavaScript 触发的导航和任何后续重定向后的最终 URL 10。

如果 openurl('page1') 函数不立即导航，而是执行 AJAX 调用以更新当前页面，然后需要后续交互才能触发导航，那么 Crawl4AI 的 session_id 功能就变得至关重要 10。通过使用 session_id，浏览器上下文（包括 cookie、本地存储和当前 DOM 状态）在多次 arun() 调用之间得以保留。这允许在同一浏览器会话中链接复杂的交互（例如，点击、等待内容、再次点击以导航），使其适用于超出单个直接 onclick 重定向的多步骤工作流程。这扩展了解决方案对更复杂 Web 应用程序的适用性。6. 高级考量与最佳实践在处理 JavaScript 驱动的动态网页抓取时，除了基本方法外，还有一些高级考量和最佳实践可以显著提高抓取任务的鲁棒性和效率。
处理弹出窗口或新标签页：
如果 openurl 函数使用 window.open() 来打开新页面，Crawl4AI（通过 Playwright）能够检测并与新的浏览器上下文（标签页/窗口）进行交互 8。虽然 result.url 仍将提供当前页面的 URL，但处理新标签页可能需要在 Crawl4AI 的钩子（hooks）或会话管理中编写特定的逻辑。
鲁棒的等待策略：
与使用固定的 setTimeout 延迟相比，优先使用 CrawlerRunConfig 的 wait_for 选项更为可靠 2。

wait_for_selector：等待特定的 CSS 选择器出现在 DOM 中，这表明内容已加载 2。
wait_for_function：等待自定义 JavaScript 函数返回一个真值，为复杂条件提供最大的灵活性 2。


多步骤流程的会话管理：
对于 openurl 是更大工作流程（例如，登录、点击、然后导航）一部分的场景，BrowserConfig 和 CrawlerRunConfig 中的 session_id 参数允许在多次 arun() 调用中保持相同的浏览器上下文 10。这对于保留状态（如认证令牌）和执行顺序操作至关重要。
错误处理与调试：

监控 result.success 和 result.error_message 以了解抓取失败的原因 12。
在开发过程中，使用 BrowserConfig(headless=False, verbose=True) 可以可视化地观察浏览器的操作，从而帮助调试 JavaScript 问题 13。
如果页面加载缓慢，调整 page_timeout 参数 11。


缓存：
注意 CacheMode 的设置。对于动态内容，通常需要将 CacheMode.BYPASS 设置为绕过缓存，以确保在交互后获取到最新数据 12。
CrawlerRunConfig 中的各种参数（如 js_code、wait_for、session_id、cache_mode）并非孤立的功能；它们协同工作以有效管理浏览器状态。例如，js_code 改变页面，wait_for 确保改变完成，session_id 在多次此类改变中保持上下文，而 cache_mode 确保始终捕获最新状态。这种全面的配置视图对于掌握 Crawl4AI 以处理复杂的动态网站至关重要，它超越了简单的“点击并获取 URL”方法，转向更复杂的“管理浏览器工作流并提取最终状态”策略。动态网页抓取通常涉及试错，因为网站实现存在变数。建议在调试时使用 headless=False 和 verbose=True 13 不仅仅是一个调试技巧；它是一种主动策略，用于理解脚本可能失败的原因。实时观察浏览器交互可以立即提供视觉反馈，了解 JavaScript 是否正确执行、元素是否被找到，或者导航是否确实按预期发生。这种实践调试方法对于快速迭代和优化高度动态网站的抓取逻辑非常宝贵。下表总结了 CrawlerRunConfig 中用于动态抓取的关键参数：表 2：动态抓取中关键的 CrawlerRunConfig 参数参数描述动态内容的主要用例与 onclick 抓取的相关性js_code注入并执行自定义 JavaScript 代码。模拟点击、表单填写、滚动等用户交互。模拟 onclick 触发的点击行为。wait_for暂停执行，直到满足特定条件。确保导航完成、新内容加载或特定元素出现。在 onclick 触发导航后，等待页面加载完成。session_id在多次抓取请求中保持相同的浏览器会话。处理多步骤交互、登录认证、分页等。保持登录状态或在复杂流程中连续操作。cache_mode控制 Crawl4AI 的缓存行为。BYPASS 模式确保在动态更改后获取最新数据。确保每次抓取都获取最新的页面状态，而非缓存。java_script_enabled启用或禁用 JavaScript 执行。必须为 True 才能执行 JavaScript 代码。必须启用，否则 onclick 事件不会触发。page_timeout页面加载或 JavaScript 执行的最大等待时间。防止因页面加载缓慢或脚本执行问题导致的无限等待。为 onclick 触发的导航设置合理的最大等待时间。7. 结论：精通 Crawl4AI 的动态网页抓取Crawl4AI 通过利用其完整的浏览器渲染能力和 js_code 执行功能，有效地解决了 onclick JavaScript 导航的挑战。它能够像真实用户一样与网页进行交互，执行客户端脚本，并准确地追踪由这些交互引起的页面重定向。本报告的核心发现总结如下：
最终 URL 的确定性来源：CrawlResult.url 属性是 JavaScript 触发导航后获取最终 URL 的权威来源 12。Crawl4AI 自动处理了所有重定向和动态 URL 变更，为用户提供了清晰的最终目标。
模拟点击与同步的关键：正确使用 js_code 来模拟点击操作，并结合 wait_for 条件进行同步，是成功抓取动态内容的基石 11。这确保了在数据提取时，页面已达到预期的稳定状态。
浏览器自动化复杂性的抽象：Crawl4AI 极大地抽象了浏览器自动化的底层复杂性，使得动态网页抓取对开发者而言更加易于实现。它将繁琐的浏览器事件处理和状态管理封装起来，让开发者能够专注于数据本身。
Crawl4AI 的价值主张在于其作为一款 AI 就绪（AI-ready）的网页抓取工具的强大能力。它能够处理现代 Web 应用程序的复杂性，提供干净、结构化的数据，以供下游的 AI/LLM 管道使用 1。随着 Web 技术不断向更动态和交互式的体验发展，对 Crawl4AI 这样能够模拟真实用户行为并处理复杂 JavaScript 驱动导航的先进抓取工具的需求将持续增长。                    

all_urls.append(new_url)
改为｛source:'第 {page_num + 1} 页第 {i+1} 个元素',name:'{title}',url:{new_url}｝

[{'source': '第 5 页第 19 个元素', 'name': '重庆市南岸区天台岗小学校南湖校区教学辅助用房改建工程', 'url': 'https://www.cqggzy.com/jumpnew.html?infoid=42507af7-fd56-431e-ac80-5beebef1b457&categorynum=004002009001'},
元素 100: {'source': '第 5 页第 20 个元素', 'name': '江北区大石坝组团K12-4号地块项目(二期)限价编制', 'url': 'https://www.cqggzy.com/jumpnew.html?infoid=33384b19-647c-4949-8358-bb3b888331b4&categorynum=004002004001'}]