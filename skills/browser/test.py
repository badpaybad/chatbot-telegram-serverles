import asyncio
from playwright.async_api import async_playwright

import random

async def run_browser_agent():
    async with async_playwright() as p:
        # 1. Khởi chạy trình duyệt (headless=False để quan sát)
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            # 2. Đi tới trang Login
            print("Đang mở trang đăng nhập...")
            await page.goto("https://static.airobotics.vn/games/maths/")

            # 3. Nhập liệu (Playwright tự đợi selector này xuất hiện)
            await page.fill('input[id="inputA"]', f"{random.randint(0, 1000) }")
            await page.fill('input[id="inputB"]', f"{random.randint(0, 1000) }")

            # 4. Click Submit và đợi chuyển hướng (Redirect)
            print("Đang nhấn đăng nhập và đợi chuyển hướng...")
            # Playwright có cơ chế thông minh: nhấn và đợi URL thay đổi
            await asyncio.gather(
                page.click('#checkBtn'),
                #page.wait_for_url("**/dashboard", timeout=10000) # Đợi tới khi URL chứa chữ 'dashboard'
            )

            # # 5. Đợi nội dung ở trang mới load xong
            # print(f"Đã tới trang: {page.url}")
            # await page.wait_for_selector(".balance-amount") 

            # # 6. Lấy dữ liệu (Scraping)
            # balance = await page.inner_text(".balance-amount")
            # print(f"Dữ liệu lấy được: {balance}")

            # # Lấy cấu trúc trang web dưới dạng đơn giản nhất để AI đọc
            # snapshot = await page.accessibility.snapshot()
            # print(snapshot)

            # 7. Chụp ảnh làm bằng chứng cho AI Agent
            await page.screenshot(path="dashboard_result.png")
            print("Done")

        except Exception as e:
            print(f"Lỗi rồi: {e}")
        finally:
            await browser.close()

asyncio.run(run_browser_agent())