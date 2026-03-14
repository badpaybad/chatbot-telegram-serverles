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
            #     #page.wait_for_url("**/dashboard", timeout=5000) # Đợi tới khi URL chứa chữ 'dashboard'
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

async def page_scroll():
    async with browser_lock:
        try:
            await page.wait_for_load_state("networkidle", timeout=5000)
        except Exception:
            pass
        for _ in range(3):
            try:
                await asyncio.wait_for(page.evaluate("window.scrollTo(0, document.body.scrollHeight)"), timeout=5.0)
                # await page.keyboard.press("PageDown")
                # await asyncio.sleep(1)
                await asyncio.wait_for(page.evaluate("window.scrollTo(0, 0)"), timeout=5.0)
                await page.keyboard.press("PageUp")
                await asyncio.sleep(1)
            except Exception:
                pass
        for _ in range(3):
            try:
                await asyncio.wait_for(page.evaluate("window.scrollTo(0, document.body.scrollHeight)"), timeout=5.0)
                await page.keyboard.press("PageDown")
                await asyncio.sleep(1)
                # await asyncio.wait_for(page.evaluate("window.scrollTo(0, 0)"), timeout=5.0)
                # await page.keyboard.press("PageUp")
                # await asyncio.sleep(1)
            except Exception:
                pass
    pass

async def open_zalo_web():

    async with browser_lock:
        print("Đang mở trang đăng nhập...")
        try:
            await page.goto("https://chat.zalo.me/", timeout=15000)
            await page.wait_for_load_state("networkidle", timeout=5000)
        except Exception as e:
            print(f"Lỗi khi open_zalo_web: {e}")
    await page_scroll()

async def download_qr_code():

    async with browser_lock:
        try:
            await page.wait_for_load_state("networkidle", timeout=5000)
        except Exception:
            pass
    await page_scroll()

    file_name="zalo_qr.png"
    # 1. Tìm selector: tìm img bên trong class .qr-container
    qr_selector = ".qr-container img"
    
    try:
        # Đợi QR xuất hiện
        # await page.wait_for_selector(qr_selector, timeout=5000)
        
        async with browser_lock:
            # 2. Lấy thuộc tính src của thẻ img
            try:
                qr_src = await page.locator(qr_selector).get_attribute("src", timeout=5000)
            except:
                qr_src = None
                    
        if not qr_src:
            print("Không tìm thấy thuộc tính src của QR")

            try:    
                async with browser_lock:
                    await page.get_by_text("Đã hiểu").click(force=True, timeout=5000)    
                    print(f"Click nút Đã hiểu") 

                await asyncio.sleep(3)
            except Exception as e:
                print(f"Không tìm thấy nút Đã hiểu")
            

            async with browser_lock:
                qr_src = await page.locator(qr_selector).get_attribute("src", timeout=5000)    

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
        try:
            await page.wait_for_load_state("networkidle", timeout=5000)
        except Exception:
            pass
        
    await page_scroll()
    try:
        # z--btn--v2 btn-primary small sync-v2-ok suggestNewSync --rounded sync-v2-ok suggestNewSync
        # await page.locator(".suggestNewSync.btn-primary", timeout=5000).click(force=True)

        async with browser_lock:
            # Đợi cho tới khi DOM của trang mới thực sự sẵn sàng
            await page.wait_for_selector(".sync-v2-banner.suggestNewSync", state="attached", timeout=5000)
            await page.locator(".sync-v2-banner.suggestNewSync").click(force=True, timeout=5000)

    except Exception as e:
        print(f"Không tìm thấy nút Đồng bộ ngay .suggestNewSync.btn-primary")
    try:
        # tds-conversation__footer-content-sync-button
        async with browser_lock:
            await page.wait_for_selector(".tds-conversation__footer-content-sync-button", state="attached", timeout=5000)
            await page.locator(".tds-conversation__footer-content-sync-button").click(force=True, timeout=5000)

    except Exception as e:
        print(f"Không tìm thấy nút Đồng bộ ngay .tds-conversation__footer-content-sync-button")

    try:
        async with browser_lock:
            await page.get_by_text("Nhấn để đồng bộ ngay", timeout=5000).click(force=True)    
            print(f"Click nút Nhấn để đồng bộ ngay") 

        await asyncio.sleep(3)
    except Exception as e:
        print(f"Không tìm thấy nút Nhấn để đồng bộ ngay")
    try:
        async with browser_lock:
            await page.get_by_text("Đồng bộ ngay", timeout=5000).click(force=True)    
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
                    found=await page.wait_for_selector(qr_selector, timeout=5000)
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
        try:
            await page.wait_for_load_state("networkidle", timeout=5000)
        except Exception:
            pass
    
    await page_scroll()

    # https://id.zalo.me/account?continue=https%3A%2F%2Fchat.zalo.me%2F

    # qr_file=await download_qr_code()
    qr_file=None

    qr_selector = ".fa-Contact_28_Line"
    while not isStop:
        try:
            async with browser_lock:
                found=await page.wait_for_selector(qr_selector, timeout=5000)
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
        try:
            await page.wait_for_load_state("networkidle", timeout=5000)
        except Exception:
            pass
    
    await page_scroll()
    try:
        print(f"Opening group: {groupname}")

        async with browser_lock:
            try:
                search_input = page.locator('#contact-search-input')
                await search_input.fill(groupname, timeout=5000)
                await search_input.press('Enter', timeout=5000)
                await asyncio.sleep(1)
            except Exception as e:
                print(f"Error searching for groupname: {e}")

        is_found = False
        found = None
        # Use a more robust selector or exact text text=
        selectorGroupname = f'span.truncate:has-text("{groupname}"), div.truncate:has-text("{groupname}")'

        while not is_found and not isStop:
            async with browser_lock:
                container_scroll = page.locator('#conversationListId').first
                if await container_scroll.count() > 0:
                    print("Đang cuộn #conversationListId để tìm group...")
                    if not is_found:
                        # Cuộn xuống
                        for _ in range(5):
                            found = page.locator(selectorGroupname)
                            if await found.count() > 0:
                                is_found = True
                                break
                            try:
                                await asyncio.wait_for(container_scroll.evaluate('''node => {
                                    node.scrollTop += 800;
                                    if (node.parentElement) {
                                        node.parentElement.scrollTop += 800;
                                    }
                                    let children = node.querySelectorAll('*');
                                    for (let child of children) {
                                        if (child.scrollHeight > child.clientHeight) {
                                            child.scrollTop += 800;
                                        }
                                    }
                                }'''), timeout=5.0)
                                await asyncio.sleep(1)
                            except: pass
                    
                    # Cuộn lên trước vài lần
                    for _ in range(5):
                        found = page.locator(selectorGroupname)
                        if await found.count() > 0:
                            is_found = True
                            break
                        try:
                            await asyncio.wait_for(container_scroll.evaluate('''node => {
                                node.scrollTop -= 800;
                                if (node.parentElement) {
                                    node.parentElement.scrollTop -= 800;
                                }
                                let children = node.querySelectorAll('*');
                                for (let child of children) {
                                    if (child.scrollHeight > child.clientHeight) {
                                        child.scrollTop -= 800;
                                    }
                                }
                            }'''), timeout=5.0)
                            await asyncio.sleep(1)
                        except: pass
                    
                else:
                    found = page.locator(selectorGroupname)
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
                await found.click(force=True, timeout=5000)
                await found.click(force=True, timeout=5000)
                print("clicked", groupname, found)
            await asyncio.sleep(2)
        
        while not isStop:
            async with browser_lock:
                # Check for container existence before getting text

                print("đang tìm #chatViewContainer")
                container_count=0
                try:
                    # Check if it exists without waiting indefinitely
                    await page.wait_for_selector("#chatViewContainer", timeout=2000)
                    container_count = await page.locator("#chatViewContainer").count()
                except:
                    container_count = 0
                    print("Không tìm thấy #chatViewContainer")
                
                if container_count == 0 and found:
                    try:
                        await found.click(force=True, timeout=5000)
                        await found.click(force=True, timeout=5000)
                        print("clicked 2", groupname, found)
                    except Exception as e:
                        print(f"Lỗi khi click lại group lần 2: {e}")

                    await asyncio.sleep(2)

                if container_count > 0:
                    container = page.locator("#chatViewContainer")

                    print("đã tìm thấy chatViewContainer", container)
                    # # Cuộn vùng container lên xuống để load hết nội dung
                    print("Đang cuộn #chatViewContainer lên vài lần...")
                    for _ in range(5):
                        try:
                            await asyncio.wait_for(container.evaluate('''node => {
                                let scrollNode = node.querySelector('#messageViewContainer .transform-gpu');
                                if (scrollNode) {
                                    scrollNode.scrollBy({top: -2800, behavior: 'smooth'});
                                } else {
                                    node.scrollTop -= 2800;
                                    if (node.parentElement) {
                                        node.parentElement.scrollTop -= 2800;
                                    }
                                    let children = node.querySelectorAll('*');
                                    for (let child of children) {
                                        if (child.scrollHeight > child.clientHeight && window.getComputedStyle(child).overflowY !== 'hidden') {
                                            child.scrollTop -= 2800;
                                        }
                                    }
                                }
                            }'''), timeout=5.0)
                            await asyncio.sleep(1)
                        except Exception as e:
                            print(f"Lỗi khi cuộn container lên: {e}")
                            pass
                            
                    print("Đang cuộn #chatViewContainer xuống vài lần...")
                    for _ in range(6):
                        try:
                            await asyncio.wait_for(container.evaluate('''node => {
                                let scrollNode = node.querySelector('#messageViewContainer .transform-gpu');
                                if (scrollNode) {
                                    scrollNode.scrollBy({top: 2800, behavior: 'smooth'});
                                } else {
                                    node.scrollTop += 2800;
                                    if (node.parentElement) {
                                        node.parentElement.scrollTop += 2800;
                                    }
                                    let children = node.querySelectorAll('*');
                                    for (let child of children) {
                                        if (child.scrollHeight > child.clientHeight && window.getComputedStyle(child).overflowY !== 'hidden') {
                                            child.scrollTop += 2800;
                                        }
                                    }
                                }
                            }'''), timeout=5.0)
                            await asyncio.sleep(1)
                        except Exception as e:
                            print(f"Lỗi khi cuộn container xuống: {e}")
                            pass
                    

                    print("đã cuộn chatViewContainer", container)
                    break
                    # try:
                    #     text = await container.text_content(timeout=5000)
                    #     if text and len(text.strip()) > 0:
                    #         break
                    #     else:
                    #         print("Lấy được text_content nhưng nội dung trống, thử lại...")
                    # except Exception as e:
                    #     print(f"Lỗi khi lấy text_content của container: {e}")
                else:
                    if found:
                        try:
                            await found.click(force=True, timeout=5000)
                            print("clicked 3", groupname, found)
                        except Exception as e:
                            print(f"Lỗi khi click lại group lần 3: {e}")

                    await asyncio.sleep(2)
            
            await asyncio.sleep(1)

        print("chatViewContainer loaded")

        count=0
        chat_items=None
        async with browser_lock:
            chat_items = page.locator("#chatViewContainer div.chat-item")
            count = await chat_items.count()
            print(f"#chatViewContainer div.chat-item Found {count} messages.")

        listmsg=[]
        for i in range(count):
            item = chat_items.nth(i)
            listmsg.append(await item.inner_text(timeout=5000))

        return listmsg

    except Exception as e:
        print(f"Error in open_zalo_group_omt_tbp: {e}")
        return None


latest_zalo_group_msg_list_check_duplicate=[]

max_zalo_message_memory=1000

async def zalo_all_message_last_30_msg_in_db_to_check_duplicate(groupname="OMT-TBP"):

    all_messages=knowledgebase.dbcontext.zalo_all_message.search_json("groupname",groupname,limit=30)
    # rounded3= round(len(all_messages)/3)*3

    # all_messages=all_messages[:rounded3]

    print("zalo_all_message_last_30_msg_in_db_to_check_duplicate", len(all_messages))
    for dbdata in all_messages:
        json_msg=dbdata["json"]
        # await zalo_group_msg_ActionBlockQueue.put({"groupname": json_msg['groupname'], "message": json_msg['message']})

        batch_text_str = f"{json_msg['groupname']}: " + " | ".join([json_msg['message']])
        latest_zalo_group_msg_list_check_duplicate.append(batch_text_str)
    


async def process_1_zalo_msg_in_group_into_telegram(txt):
    
    try:
        batch = []
        if txt:
            batch.append(txt)
        
        # # Thử lấy thêm tối đa 2 item nữa nếu có sẵn trong queue để gom thành batch 3
        # for _ in range(2):
        #     if not zalo_group_msg_ActionBlockQueue.empty():
        #         next_txt = await zalo_group_msg_ActionBlockQueue.get()
        #         if next_txt:
        #             batch.append(next_txt)
        #     else:
        #         break
        
        if not batch:
            return

        # Gom tất cả tin nhắn trong batch để check duplicate
        all_messages = []
        for item in batch:
            all_messages.append(item["message"])
        
        group_name = batch[0]["groupname"]
        # Chuyển batch thành chuỗi duy nhất để so khớp
        batch_text_str = f"{group_name}: " + " | ".join(all_messages)

        if batch_text_str in latest_zalo_group_msg_list_check_duplicate:
            print(f"Bỏ qua batch trùng lặp ({len(batch)} items) từ {group_name}")
        else:
            # Lưu vào db
            print(f"Xử lý batch {len(batch)} items từ {group_name}: {len(all_messages)} tin nhắn")
            for msg in all_messages:
                # todo: nếu cần transform trước khi lưu db
                
                knowledgebase.dbcontext.zalo_all_message.insert({
                    "groupname": group_name,
                    "message": msg,
                    })
                # print("inserted ----->", msg)

            # Lưu vào lịch sử trùng lặp
            latest_zalo_group_msg_list_check_duplicate.append(batch_text_str)
            if len(latest_zalo_group_msg_list_check_duplicate) > max_zalo_message_memory:
                latest_zalo_group_msg_list_check_duplicate.pop(0)
        
    except Exception as e:
        print(f"Lỗi trong process_1_zalo_msg_in_group_into_telegram: {e}")



async def loop_enqueue_processed_zalo_group_msg(groupname="OMT-TBP"):
    global max_zalo_message_memory
    while not isStop:
        all_texts = await open_zalo_group_omt_tbp(groupname)
        if all_texts:
            if len(all_texts) > max_zalo_message_memory:
                max_zalo_message_memory=len(all_texts)
                print("max_zalo_message_memory", max_zalo_message_memory)
            for msg in all_texts:
                await process_1_zalo_msg_in_group_into_telegram({"groupname": groupname, "message": msg})

        await asyncio.sleep(30)
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

    zalo_group_name="OMT-TBP"

    await zalo_all_message_last_30_msg_in_db_to_check_duplicate(zalo_group_name)
    
    await asyncio.gather(
        browser_task,
        loop_enqueue_processed_zalo_group_msg(zalo_group_name)
    )

if __name__ == "__main__":
    try:
        asyncio.run(loop())
    except KeyboardInterrupt:
        isStop = True
        print("Stopping...")