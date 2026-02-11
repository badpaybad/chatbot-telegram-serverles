from telethon import TelegramClient, events
import uuid
from collections import defaultdict, deque
# https://my.telegram.org/apps
from config import TELEGRAM_API_ID, TELEGRAM_API_HASH
import asyncio
from gemini_summary import gemini_summary


# Bạn có thể cố định 1 UUID cho 1 tài khoản
session_name = "dunp-assitant-account-id-v1"

# Hoặc nếu bạn muốn tạo mới hoàn toàn (nhưng sẽ phải login lại liên tục)
# session_name = str(uuid.uuid4())


group_cache = {}

chat_events = defaultdict(lambda: deque(maxlen=100))

group_messages = defaultdict(lambda: deque(maxlen=10))

user_cache = defaultdict(lambda: deque(maxlen=100))

user_messages = defaultdict(lambda: deque(maxlen=10))

# async def main():
#     # Lấy danh sách tất cả các cuộc hội thoại (Dialogs)
#     async for dialog in client.iter_dialogs():
#         if dialog.is_group:
#             print(f"ID: {dialog.id} | Name: {dialog.name}")

# with client:
#     client.loop.run_until_complete(main())

client = None


async def run_until_disconnected():

    global client

    client = TelegramClient(session_name, TELEGRAM_API_ID, TELEGRAM_API_HASH)
    """
    Class Sự kiện	Ý nghĩa
events.NewMessage	Có tin nhắn mới được gửi đến.
events.MessageEdited	Một tin nhắn cũ bị thay đổi nội dung.
events.MessageDeleted	Một hoặc nhiều tin nhắn bị xóa.
events.ChatAction	Các thay đổi trong nhóm (vào/ra, ghim bài, đổi tên nhóm).
events.UserUpdate	Trạng thái người dùng (Online, Offline, Last Seen).
events.CallbackQuery	Khi người dùng nhấn vào các nút (Inline Buttons) của Bot
    """
    # @client.on(events.UserUpdate)
    # @client.on(events.ChatAction)
    @client.on(events.MessageDeleted)
    @client.on(events.MessageEdited)
    @client.on(events.NewMessage)
    # @client.on(events.CallbackQuery)
    async def handler(event):
        print("event===========================")
        print(event)
        print("event===========================")
        # chat_events["all"] = event

        # if event.is_group:
        #     if event.chat_id not in group_cache:
        #         chat = await event.get_chat()
        #         group_cache[event.chat_id] = chat
        #         # chat_groups[event.chat_id].title

        #     print(
        #         f"Tin nhắn mới từ: {group_cache[event.chat_id].title} (ID: {event.chat_id})")
        #     group_messages[event.chat_id].append(event)

        # # 2. TRƯỜNG HỢP CÁ NHÂN NHẮN CHO MÌNH (Inbox)
        # elif event.is_private:
        #     # event.out = False nghĩa là tin nhắn từ người khác gửi đến mình
        #     if not event.out:
        #         if event.chat_id not in user_cache:
        #             user_cache[event.chat_id] = await event.get_chat()

        #         sender = user_cache[event.chat_id]
        #         print(f"Người dùng [{sender.first_name}]")
        #         user_messages[event.chat_id].append(event)

        # # Logic tóm tắt sẽ được chạy trong một task riêng biệt

        # print(f"{event}")
        # print(f"-----------------------------------")
    print("telethon start, you will get summary interval 5 minutes in Saved messageses ...")
    await client.start()

    # # Chạy tác vụ nền để tóm tắt định kỳ
    # asyncio.create_task(periodic_summary())

    # print("Đã khởi động tác vụ tóm tắt định kỳ.")

    await client.run_until_disconnected()

    # # Gửi tóm tắt đến nhóm
    # try:
    #     await client.send_message(group_id, summary_text)

    #     # Xóa cache của nhóm này sau khi đã tóm tắt và gửi thành công
    #     if group_id in group_messages:
    #         group_messages[group_id].clear()
    #         print(f"Đã xóa cache tin nhắn cho nhóm {group_name}")

    # except Exception as e:
    #     print(f"Lỗi khi gửi tóm tắt đến nhóm {group_name}: {e}")gọi


async def send_to_saved_messages(summary_text):

    global client
# Kiểm tra xem client đã được khởi tạo từ hàm kia chưa
    if client is None:
        print("❌ Lỗi: Client chưa được khởi tạo!")
        return
    try:
        # 'me' là alias đặc biệt trong Telethon trỏ thẳng tới Saved Messages của bạn
        await client.send_message('me', summary_text)
        print("✅ Đã gửi tóm tắt vào Saved Messages")
    except Exception as e:
        print(f"❌ Lỗi khi gửi tin nhắn: {e}")


async def periodic_summary():
    """
    Periodically summarizes messages in groups.
    """
    while True:
        # Đợi 1 phút
        await asyncio.sleep(60*5)

        # --- TÓM TẮT TIN NHẮN NHÓM ---
        group_ids = list(group_messages.keys())
        print(f"group_ids count: {len(group_ids)}")
        for group_id in group_ids:
            messages_to_summarize = list(group_messages.get(group_id, []))
            if not messages_to_summarize:
                continue

            texts = []
            for msg in messages_to_summarize:
                sender_name = "Unknown"
                if msg.sender:
                    sender_name = msg.sender.first_name or msg.sender.username or "Unknown"
                if msg.raw_text:
                    texts.append(f"{sender_name}: {msg.raw_text}")

            if not texts:
                continue

            full_text = "\n".join(texts)
            group_name = group_cache.get(
                group_id).title if group_id in group_cache else group_id

            print(f"--- Đang tóm tắt cho nhóm: {group_name} ---")
            summary_text = gemini_summary(full_text)
            print(f"--- Tóm tắt cho nhóm {group_name} ---")
            print(summary_text)
            print("------------------------------------")

            await send_to_saved_messages(f"--- Tóm tắt cho nhóm: {group_name} ---\n{summary_text}")
            group_messages[group_id].clear()

        # --- TÓM TẮT TIN NHẮN CÁ NHÂN ---
        user_ids = list(user_messages.keys())
        print(f"group_ids count: {len(user_ids)}")
        for user_id in user_ids:
            messages_to_summarize = list(user_messages.get(user_id, []))
            if not messages_to_summarize:
                continue

            texts = []
            for msg in messages_to_summarize:
                sender_name = "Unknown"
                # Trong tin nhắn cá nhân, sender chính là người đó
                if msg.sender:
                    sender_name = f"{msg.sender.first_name} ({msg.sender.username})"
                if msg.raw_text:
                    texts.append(f"{sender_name}: {msg.raw_text}")

            if not texts:
                continue

            full_text = "\n".join(texts)
            user_info = user_cache.get(user_id)
            user_name = user_info.first_name if user_info else f"User ID: {user_id}"

            print(f"--- Đang tóm tắt cho người dùng: {user_name} ---")
            summary_text = gemini_summary(full_text)
            print(f"--- Tóm tắt cho người dùng {user_name} ---")
            print(summary_text)
            print("------------------------------------")

            await send_to_saved_messages(f"--- Tóm tắt từ: {user_name} ---\n{summary_text}")
            user_messages[user_id].clear()
