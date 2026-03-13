import sys
import os
# Thêm thư mục gốc vào sys.path để có thể import các module bot_telegram, config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import asyncio
from playwright.async_api import async_playwright

import random
import os
import time
import base64
import requests
import bot_telegram
import queue

import knowledgebase.dbcontext


from config import TELEGRAM_OWNER_USERID,TELEGRAM_BOT_GROUP_CHATID,HISTORY_CHAT_MAX_LEN,TELEGRAM_BOT_TOKEN, TELEGRAM_API_URL, PORT, TELEGRAM_BOT_CHATID, TELEGRAM_BOT_USERNAME, GEMINI_APIKEY,GEMINI_MODEL, DISCORD_PUBKEY, DISCORD_APPID, DISCORD_TOKEN,  TELEGRAM_API_ID, TELEGRAM_API_HASH, REPLY_ON_TAG_BOT_USERNAME

import bot_telegram

"""_summary_
các action queue vào sẽ thực hiện lần lượt, vd nếu có while true ở action trước thì đến sau sẽ đợi xong phía trước break while 
"""
browserActionBlockQueue= asyncio.Queue()
isStop=False
page=None
context=None
playwright_instance=None

browser_lock = asyncio.Lock()

async def loop_run_browser_agent():
    global browserActionBlockQueue
    global isStop
    global page
    global context
    global playwright_instance

    async with async_playwright() as p:
        playwright_instance=p
        # 1. Khởi chạy trình duyệt (headless=False để quan sát)
        # browser = await p.chromium.launch(headless=False)
        # context = await browser.new_context()
        # page = await context.new_page()
        # Playwright sẽ tự tìm Chrome trong các đường dẫn mặc định của Ubuntu

        # Lấy username để tạo đường dẫn chính xác
        user_home = os.path.expanduser("~")
        user_data_dir = f"{user_home}/.config/google-chrome/Zalo"
        print("user_data_dir",user_data_dir)

        # browser = await p.chromium.launch(channel="chrome", headless=False,
        # args=["--no-sandbox"])
        # page = await browser.new_page()

        context = await p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            channel="chrome",
            # headless=True, # chạy ngầm
            headless=False, # xem được thao tác 
            args=["--no-sandbox"] # Cần thiết nếu chạy với quyền root hoặc môi trường đặc biệt
        )
        async with browser_lock:
            page = context.pages[0] # Persistent context tạo sẵn 1 page

        try:
            # 2. Đi tới trang Login

            # 3. Nhập liệu (Playwright tự đợi selector này xuất hiện)
            # await page.fill('input[id="inputA"]', f"{random.randint(0, 1000) }")
            # await page.fill('input[id="inputB"]', f"{random.randint(0, 1000) }")

            # 4. Click Submit và đợi chuyển hướng (Redirect)
            # print("Đang nhấn đăng nhập và đợi chuyển hướng...")
            # # Playwright có cơ chế thông minh: nhấn và đợi URL thay đổi
            # await asyncio.gather(
                # page.click('#checkBtn'),
            #     #page.wait_for_url("**/dashboard", timeout=10000) # Đợi tới khi URL chứa chữ 'dashboard'
            # )

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
            # await page.screenshot(path="dashboard_result.png")

            while not isStop:

                if browserActionBlockQueue.empty():
                    await asyncio.sleep(1)
                    continue

                nextact= await browserActionBlockQueue.get()

                if nextact:
                    if asyncio.iscoroutinefunction(nextact):
                        await nextact()
                    else:
                        nextact()

            print("loop_run_browser_agent: Done")

        except Exception as e:
            print(f"Lỗi loop_run_browser_agent: {e}")
        finally:
            # await browser.close()
            await context.close()
            pass
async def open_zalo_web():

    async with browser_lock:
        print("Đang mở trang đăng nhập...")
        await page.goto("https://chat.zalo.me/")
        await page.wait_for_load_state("networkidle")
    await asyncio.sleep(3)



async def download_qr_code():

    async with browser_lock:
        await page.wait_for_load_state("networkidle")
        file_name="zalo_qr.png"
    # 1. Tìm selector: tìm img bên trong class .qr-container
    qr_selector = ".qr-container img"
    
    try:
        # Đợi QR xuất hiện
        # await page.wait_for_selector(qr_selector, timeout=10000)
        
        async with browser_lock:
            # 2. Lấy thuộc tính src của thẻ img
            qr_src = await page.locator(qr_selector).get_attribute("src")
                    
        if not qr_src:
            print("Không tìm thấy thuộc tính src của QR")

            try:    
                async with browser_lock:
                    await page.get_by_text("Đã hiểu").click(force=True)    
                    print(f"Click nút Đã hiểu") 

                await asyncio.sleep(3)
            except Exception as e:
                print(f"Không tìm thấy nút Đã hiểu")
            

            async with browser_lock:
                qr_src = await page.locator(qr_selector).get_attribute("src", timeout=10000)    

            if not qr_src:
                print("Không tìm thấy thuộc tính src của QR")
            return None

        # 3. Xử lý nếu là Base64 (Zalo thường dùng cái này cho QR)
        if "base64," in qr_src:
            header, encoded = qr_src.split(",", 1)
            data = base64.b64decode(encoded)
            with open(file_name, "wb") as f:
                f.write(data)
            print(f"Đã lưu QR từ Base64: {file_name}")
            
        # 4. Xử lý nếu là URL thông thường
        else:
            response = requests.get(qr_src)
            if response.status_code == 200:
                with open(file_name, "wb") as f:
                    f.write(response.content)
                print(f"Đã tải QR từ URL: {file_name}")

        return file_name
    except Exception as e:
        print(f"Lỗi khi tải QR: {e}")

        return None

async def sync_zalo_chats_groups():
    print("sync_zalo_chats_groups doing")

    async with browser_lock:
        await page.wait_for_load_state("networkidle")
    await asyncio.sleep(3)
    try:
        # z--btn--v2 btn-primary small sync-v2-ok suggestNewSync --rounded sync-v2-ok suggestNewSync
        # await page.locator(".suggestNewSync.btn-primary", timeout=10000).click(force=True)

        async with browser_lock:
            # Đợi cho tới khi DOM của trang mới thực sự sẵn sàng
            await page.wait_for_selector(".sync-v2-banner.suggestNewSync", state="attached", timeout=10000)
            await page.locator(".sync-v2-banner.suggestNewSync").click(force=True)

    except Exception as e:
        print(f"Không tìm thấy nút Đồng bộ ngay .suggestNewSync.btn-primary")
    try:
        # tds-conversation__footer-content-sync-button
        async with browser_lock:
            await page.wait_for_selector(".tds-conversation__footer-content-sync-button", state="attached", timeout=10000)
            await page.locator(".tds-conversation__footer-content-sync-button").click(force=True)

    except Exception as e:
        print(f"Không tìm thấy nút Đồng bộ ngay .tds-conversation__footer-content-sync-button")

    try:
        async with browser_lock:
            await page.get_by_text("Nhấn để đồng bộ ngay", timeout=10000).click(force=True)    
            print(f"Click nút Nhấn để đồng bộ ngay") 

        await asyncio.sleep(3)
    except Exception as e:
        print(f"Không tìm thấy nút Nhấn để đồng bộ ngay")
    try:
        async with browser_lock:
            await page.get_by_text("Đồng bộ ngay", timeout=10000).click(force=True)    
            print(f"Click nút Đồng bộ ngay") 

        await asyncio.sleep(3)
    except Exception as e:
        print(f"Không tìm thấy nút Đồng bộ ngay")

    try:
        #sync-message-popup
            
        qr_selector = ".sync-message-popup"
        while not isStop:
            try:
                async with browser_lock:
                    found=await page.wait_for_selector(qr_selector, timeout=10000)
                if found:
                    print("Đang đồng bộ")
                    await asyncio.sleep(10)

                    print("Vẫn đang hiện .sync-message-popup")
                    await bot_telegram.send_telegram_message(TELEGRAM_OWNER_USERID,f"Vẫn đang hiện .sync-message-popup, bạn mở zalo để đồng ý đồng bộ")
                    await asyncio.sleep(10)
            except Exception as ex:

                print(f"Không có .sync-message-popup -> đã đồng bộ: {ex}")
                
                break 
                
                pass
    except:
        pass

async def check_zalo_qr_auth():

    async with browser_lock:
        await page.wait_for_load_state("networkidle")

    # https://id.zalo.me/account?continue=https%3A%2F%2Fchat.zalo.me%2F

    # qr_file=await download_qr_code()
    qr_file=None

    qr_selector = ".fa-Contact_28_Line"
    while not isStop:
        try:
            async with browser_lock:
                found=await page.wait_for_selector(qr_selector, timeout=10000)
            if found:
                print("QR code đã ẩn, đã vào trang chat")

                return 
            else:
                print(f"Redownload QR để check qr_selector: {qr_selector}")
                if not qr_file:
                    qr_file=await download_qr_code()
                    print("Redownload QR")
                else:
                    print("QR code download xong, cần đăng nhập bằng điện thoại để vào trang chat")
                    await bot_telegram.send_telegram_message(TELEGRAM_OWNER_USERID,f"QR code download xong, cần đăng nhập bằng điện thoại để vào trang chat", 
                    files=[qr_file])
                    await asyncio.sleep(5)      
                    
            await asyncio.sleep(3)               
        except Exception as ex:
            print(f"check_zalo_qr_auth Lỗi khi check QR: {ex}")
            # case timeout dom selector

            print(f"Redownload QR để check qr_selector: {qr_selector}")
            if not qr_file:
                qr_file=await download_qr_code()
                print("Redownload QR")
            else:
                print("QR code download xong, cần đăng nhập bằng điện thoại để vào trang chat")
                await bot_telegram.send_telegram_message(TELEGRAM_OWNER_USERID,f"QR code download xong, cần đăng nhập bằng điện thoại để vào trang chat", 
                files=[qr_file])
                await asyncio.sleep(5) 

            await asyncio.sleep(3)
       
        pass

async def open_zalo_group_omt_tbp(groupname:str="OMT-TBP"):
    async with browser_lock:
        await page.wait_for_load_state("networkidle")
    try:
        print(f"Opening group: {groupname}")

        is_found = False
        found = None
        selectorGroupname = f'div.truncate:has-text("{groupname}")'

        while not is_found and not isStop:
            async with browser_lock:
                found = page.locator(selectorGroupname)
                #found = page.get_by_text("OMT-TBP").filter(has=page.locator("div.truncate"))
                is_found = await found.count() > 0
            
            if is_found:
                print(f"Group {groupname} found", found)
                break
            else:
                print(f"Group {groupname} not found, syncing...")
                await sync_zalo_chats_groups()
                await asyncio.sleep(5)
    
        if is_found:
            async with browser_lock:
                # conv-item-title__name truncate grid-item
                await found.click(force=True, timeout=10000)
                print("clicked", groupname, found)
            await asyncio.sleep(2)
        
        while not isStop:
            async with browser_lock:
                # Check for container existence before getting text

                print("đang tìm #messageViewContainer")
                container = page.locator("div#messageViewContainer")
                if not container and found:
                    await found.click(force=True, timeout=10000)
                    print("clicked 2", groupname, found)

                    await asyncio.sleep(2)

                if await container.count() > 0:
                    text = await container.text_content(timeout=10000)
                    if text:
                        break
                else:
                    await found.click(force=True, timeout=10000)
                    print("clicked 2", groupname, found)

                    await asyncio.sleep(2)
            
            await asyncio.sleep(1)

        print("messageViewContainer loaded")

        count=0
        chat_items=None
        async with browser_lock:
            chat_items = page.locator("div#messageViewContainer div.chat-item")
            count = await chat_items.count()
            print(f"Found {count} messages.")

        listmsg=[]
        for i in range(count):
            item = chat_items.nth(i)
            listmsg.append(await item.inner_text(timeout=10000))

        return listmsg

    except Exception as e:
        print(f"Error in open_zalo_group_omt_tbp: {e}")
        return None

zalo_group_msg_ActionBlockQueue= asyncio.Queue()

latest_zalo_group_msg_list_check_duplicate=[]

async def loop_enqueue_processed_zalo_group_msg():
    while not isStop:
        all_texts = await open_zalo_group_omt_tbp("OMT-TBP")
        if all_texts:
            await zalo_group_msg_ActionBlockQueue.put({"groupname": "OMT-TBP", "message": all_texts})
        await asyncio.sleep(10)
    pass


async def loop_dequeue_processed_zalo_group_msg_into_telegram():
    while not isStop:
        try:
            batch = []
            # Chờ lấy ít nhất 1 item từ queue
            txt = await zalo_group_msg_ActionBlockQueue.get()
            if txt:
                batch.append(txt)
            
            # Thử lấy thêm tối đa 2 item nữa nếu có sẵn trong queue để gom thành batch 3
            for _ in range(2):
                if not zalo_group_msg_ActionBlockQueue.empty():
                    next_txt = await zalo_group_msg_ActionBlockQueue.get()
                    if next_txt:
                        batch.append(next_txt)
                else:
                    break
            
            if not batch:
                continue

            # Gom tất cả tin nhắn trong batch để check duplicate
            all_messages = []
            for item in batch:
                all_messages.extend(item["message"])
            
            group_name = batch[0]["groupname"]
            # Chuyển batch thành chuỗi duy nhất để so khớp
            batch_text_str = f"{group_name}: " + " | ".join(all_messages)

            if batch_text_str in latest_zalo_group_msg_list_check_duplicate:
                print(f"Bỏ qua batch trùng lặp ({len(batch)} items) từ {group_name}")
            else:
                # Lưu vào db
                print(f"Xử lý batch {len(batch)} items từ {group_name}: {len(all_messages)} tin nhắn")
                for msg in all_messages:
                    knowledgebase.dbcontext.zalo_all_message.insert({
                        "group": group_name,
                        "message": msg,
                        "timestamp": time.time(),
                })

                # Lưu vào lịch sử trùng lặp
                latest_zalo_group_msg_list_check_duplicate.append(batch_text_str)
                if len(latest_zalo_group_msg_list_check_duplicate) > 20:
                    latest_zalo_group_msg_list_check_duplicate.pop(0)


            
            # Đánh dấu hoàn thành cho tất cả item trong batch
            for _ in range(len(batch)):
                zalo_group_msg_ActionBlockQueue.task_done()

        except Exception as e:
            print(f"Lỗi trong loop_dequeue: {e}")
            await asyncio.sleep(1)
    pass

async def loop():
    global isStop
    
    # 1. Start browser agent FIRST
    browser_task = asyncio.create_task(loop_run_browser_agent())
    
    # 2. Wait for page to be initialized
    print("Waiting for browser to initialize...")
    while page is None:
        if isStop: return
        await asyncio.sleep(0.5)
    
    # 3. Queue initial tasks
    await browserActionBlockQueue.put(open_zalo_web)
    await browserActionBlockQueue.put(check_zalo_qr_auth)
    await browserActionBlockQueue.put(sync_zalo_chats_groups)

    print("Browser initialized and tasks queued. Starting scraping loops...")
    
    await asyncio.gather(
        browser_task,
        loop_enqueue_processed_zalo_group_msg(),
        loop_dequeue_processed_zalo_group_msg_into_telegram()
    )

if __name__ == "__main__":
    try:
        asyncio.run(loop())
    except KeyboardInterrupt:
        isStop = True
        print("Stopping...")