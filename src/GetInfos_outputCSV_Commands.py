print("脚本开始执行")

import asyncio
import csv
import json
import os
from playwright.async_api import async_playwright


async def scroll_and_collect(page, mainurl, csv_path, seen_urls):
    unchanged_count = 0
    last_height = 0
    distance = 500
    max_unchanged = 20
    scroll_count = 0
    max_scroll_times = 100

    while unchanged_count < max_unchanged and scroll_count < max_scroll_times:
        print(f"第{scroll_count+1}次滚动，已收集{len(seen_urls)}条数据")
        items = await page.evaluate(
            """(mainurl) => {
                const cards = document.querySelectorAll('.sc-1hmcekv-9.fQwEhd');
                const arr = [];
                cards.forEach(card => {
                    const titleEl = card.querySelector('a.sc-1ddd11y-0.liVXAs.sc-1hmcekv-11.eWNHVP');
                    const title = titleEl?.innerText || '';
                    const url = titleEl ? (mainurl + titleEl.getAttribute('href')) : '';
                    const category = card.querySelector('a.sc-1ddd11y-0.liVXAs.sc-1hmcekv-13.sc-1hmcekv-14.eRFArc.cZpugY')?.innerText || '';
                    const views = card.querySelector('a.sc-1ddd11y-0.hflitU')?.innerText || '';
                    const upload_time = card.querySelector('a.sc-1ddd11y-0.liVXAs.sc-1hmcekv-13.sc-1hmcekv-15.eRFArc.dehCaF')?.innerText || '';
                    arr.push({ title, url, category, views, upload_time });
                });
                return arr;
            }""",
            mainurl
        )

        new_count = 0
        with open(csv_path, 'a', encoding='utf-8', newline='') as f_csv, \
             open('Danmaku_Commands.txt', 'a', encoding='utf-8') as f_txt:
            writer = csv.writer(f_csv, quoting=csv.QUOTE_ALL)
            for item in items:
                if not item['url'] or item['url'] in seen_urls:
                    continue
                seen_urls.add(item['url'])
                writer.writerow([
                    item['url'],
                    item['title'],
                    item['category'],
                    item['views'],
                    item['upload_time']
                ])
                f_txt.write(f'python openrec_comment_Re-V3.py "{item["url"]}" "{item["upload_time"]}_{item["title"]}"\n')
                new_count += 1
        print(f"本次新增{new_count}条")

        await page.evaluate(f"window.scrollBy(0, {distance});")
        scroll_count += 1
        new_height = await page.evaluate('document.body.scrollHeight')
        if new_height == last_height:
            unchanged_count += 1
        else:
            unchanged_count = 0
            last_height = new_height
        await asyncio.sleep(2)







async def main(mainurl, targeturl, cookies_path, chromium_path):
    print(f"mainurl: {mainurl}")
    print(f"targeturl: {targeturl}")
    print(f"cookies_path: {cookies_path}")
    # 只处理单个 mainurl 和 targeturl
    lines = [{'mainurl': mainurl, 'targeturl': targeturl}]
    cookies = []
    if os.path.exists(cookies_path):
        try:
            with open(cookies_path, 'r', encoding='utf-8') as f:
                cookies = json.load(f)
            print(f"已加载cookies，共{len(cookies)}条")
        except Exception as e:
            print('cookies 文件解析失败:', e)
    else:
        print("未找到cookies文件")


    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'result.csv')
    if not os.path.exists(csv_path):
        with open(csv_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['url', 'title', 'category', 'views', 'upload_time'])
        print(f"已创建CSV文件: {csv_path}")



    async with async_playwright() as p:
        print("启动浏览器...")
        browser = await p.chromium.launch(headless=False, executable_path=chromium_path, timeout=500000)

        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
        )
        # 修正 cookies
        if cookies:
            valid_same_site = {"Strict", "Lax", "None"}
            cookies_fixed = []
            for c in cookies:
                c = c.copy()
                if "sameSite" in c:
                    if c["sameSite"] in valid_same_site:
                        pass
                    elif c["sameSite"].lower() == "no_restriction":
                        c["sameSite"] = "None"
                    else:
                        c.pop("sameSite")
                cookies_fixed.append(c)
            await context.add_cookies([
                {
                    "name": c["name"],
                    "value": c["value"],
                    "domain": c.get("domain", ""),
                    "path": c.get("path", "/"),
                    "expires": c.get("expirationDate", c.get("expires", -1)),
                    "httpOnly": c.get("httpOnly", False),
                    "secure": c.get("secure", False),
                    **({"sameSite": c["sameSite"]} if "sameSite" in c else {})
                } for c in cookies_fixed
            ])
            print("已设置cookies")
        # ----------- 下面是新增的抓取部分 -----------
        for item in lines:
            mainurl = item['mainurl']
            targeturl = item['targeturl']
            print(f"打开页面: {targeturl}")
            page = await context.new_page()
            await page.set_extra_http_headers({'referer': mainurl})
            try:
                await page.goto(targeturl, wait_until='networkidle', timeout=500000)
                seen_urls = set()
                await scroll_and_collect(page, mainurl, csv_path, seen_urls)
                print(f'已抓取: {targeturl}，共{len(seen_urls)}条')
            except Exception as e:
                print(f'抓取失败: {targeturl}', e)
            await page.close()
        await browser.close()
        print('全部抓取完成。')
    

if __name__ == "__main__":
    # 测试用参数，实际部署时可删除或修改
    mainurl = "https://www.openrec.tv"
    targeturl = "https://www.openrec.tv/user/aiba_derby"
    cookies_path = "cookies.json"
    asyncio.run(main(mainurl, targeturl, cookies_path))