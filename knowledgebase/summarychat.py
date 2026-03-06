import os
import datetime
import pickle
import json
import numpy as np
import faiss
import pandas as pd
from pypdf import PdfReader
from docx import Document
from pptx import Presentation
from google import genai
from google.genai import types
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_API_URL, PORT, TELEGRAM_BOT_CHATID, TELEGRAM_BOT_USERNAME,GEMINI_MODEL, GEMINI_APIKEY, DISCORD_PUBKEY, DISCORD_APPID, DISCORD_TOKEN,  TELEGRAM_API_ID, TELEGRAM_API_HASH, REPLY_ON_TAG_BOT_USERNAME

from typing import Any ,List, Dict
import telegram_types
import threading
import queue
import time
import knowledgebase.dbcontext
import bot_telegram
import asyncio
class SummaryChat:
    def __init__(self, batch_size=10):
        self.queue = queue.Queue()
        self.client = genai.Client(api_key=GEMINI_APIKEY)
        self.db = knowledgebase.dbcontext.db_summary_chat
        self.batch_size = batch_size
        self.chat_buffers = {} # dict: chat_id -> list of (update_obj, formatted_string)
        self.running = True
        self.thread = threading.Thread(target=self._thread_entry, daemon=True)
        self.thread.start()

    def _thread_entry(self):
            """Hàm này chạy trong Thread mới, thiết lập môi trường async"""
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Chạy hàm async loop cho đến khi kết thúc
            loop.run_until_complete(self._process_loop())
            loop.close()
            
    def enqueue_update(self, update_obj:telegram_types.TelegramUpdate|Any):
        """
        Enqueue a Telegram update object for processing.
        """
        self.queue.put(update_obj)

    def _format_message(self, update:telegram_types.TelegramUpdate|Any):
        try:
            message = update.message
            if not message:
                return None
            
            from_user = message.from_user
            first_name = from_user.first_name
            last_name = from_user.last_name
            full_name = f"{first_name} {last_name}".strip()
            
            chat = message.chat
            chat_title = chat.title
            
            date_raw = message.date
            dt = datetime.datetime.fromtimestamp(date_raw) if date_raw else datetime.datetime.now()
            dt_str = dt.strftime("%Y-%m-%d %H:%M:%S")
            
            text = message.text
            if not text:
                return None
                
            return f"{full_name} ở nhóm {chat_title} lúc {dt_str} nội dung: {text}"
        except Exception as e:
            print(f"Error formatting message: {e}")
            return None

    async def _insert_or_update_telegram_user(self, msg: telegram_types.TelegramUpdate):
        users= msg.get_users_mention()

        fromuser= msg.get_from_user()
        user_id = fromuser.id if fromuser else None
        first_name = fromuser.first_name if fromuser else None
        last_name = fromuser.last_name if fromuser else None
        is_bot = fromuser.is_bot if fromuser else None
        username = fromuser.username if fromuser else None
        fullname=f"{first_name} {last_name}"

        users.append( {
            "id": user_id,
            "username": username.replace("@",""),
            "fullname": fullname,
            "is_bot": is_bot,
            "first_name": first_name,
            "last_name": last_name
        })

        for u in users:
            if u["id"]==None and not u["username"]:
                ut= await bot_telegram.get_user_info(u["username"])
                if ut:
                    knowledgebase.dbcontext.db_telegram_user.insert(ut)
                continue
            existed = knowledgebase.dbcontext.db_telegram_user.search_json("id",u["id"])
            if not existed or len(existed)==0:
                knowledgebase.dbcontext.db_telegram_user.insert(u)
                pass
            pass

        pass

    async def _process_loop(self):
        while self.running:
            try:
                # Wait for items, timeout to check self.running
                update_obj:telegram_types.TelegramUpdate = self.queue.get(timeout=5)

                # asyncio.run(self._insert_or_update_telegram_user(update_obj))
                await self._insert_or_update_telegram_user(update_obj)

                formatted = self._format_message(update_obj)
                if formatted:
                    chat_id = update_obj.get_chat_id()
                    if chat_id:
                        if chat_id not in self.chat_buffers:
                            self.chat_buffers[chat_id] = []
                        
                        self.chat_buffers[chat_id].append((update_obj, formatted))
                        
                        if len(self.chat_buffers[chat_id]) >= self.batch_size:
                            batch = self.chat_buffers[chat_id]
                            self.chat_buffers[chat_id] = [] # Clear buffer for this chat
                            self._summarize_and_save(batch)
                self.queue.task_done()
            except queue.Empty:
                if not self.running:
                    break
                continue
            except Exception as e:
                print(f"Error in process loop: {e}")

    def _summarize_and_save(self, batch:list[telegram_types.TelegramUpdate]):
        try:
            # batch is list of (update_obj, formatted_string)
            firstchat:telegram_types.TelegramUpdate = batch[0][0]
            chat_id = firstchat.get_chat_id()
            
            # Use the date of the first message in batch for chat_datetime or range
            first_date = firstchat.get_message_date()
            dt = datetime.datetime.fromtimestamp(first_date) if first_date else datetime.datetime.now()
            
            combined_text = "\n\n".join([item[1] for item in batch])
            
            prompt = f"Hãy tóm tắt lại nội dung cuộc trò chuyện sau đây một cách ngắn gọn và súc tích:\n\n{combined_text}"
            
            response = self.client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt
            )
            
            summary_text = response.text
            
            self.db.insert({"chat_id": chat_id, "at": int(dt.timestamp()), "summary": summary_text})
            print(f"Saved summary for chat {chat_id}")
            
        except Exception as e:
            print(f"Error summarizing batch: {e}")

    def stop(self):
        self.running = False
        if self.thread.is_alive():
            # No easy way to wake up from queue.get(timeout=5) immediately other than wait
            pass