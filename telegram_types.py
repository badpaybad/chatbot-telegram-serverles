
from pydantic import BaseModel, Field,ConfigDict
import re
from typing import Any,List,Optional
# --- ĐỊNH NGHĨA DỮ LIỆU (Pydantic Models) ---
# Giúp code sạch hơn và tự động kiểm tra dữ liệu đầu vào

class AcceptedGiftTypes(BaseModel):
    unlimited_gifts: bool|None=None
    limited_gifts: bool|None=None
    unique_gifts: bool|None=None
    premium_subscription: bool|None=None
    gifts_from_channels: bool|None=None

class Chat(BaseModel):
    id: int| None = None
    first_name: str | None = None
    title: str | None = None  # Dành cho Group
    type: str | None = None
    all_members_are_administrators:bool|None=None
    accepted_gift_types: AcceptedGiftTypes|None=None


class PhotoSize(BaseModel):
    file_id: str| None = None
    file_unique_id: str| None = None
    width: int| None = None
    height: int| None = None
    file_size: int | None = None


class Document(BaseModel):
    file_id: str| None = None
    file_unique_id: str| None = None
    file_name: str | None = None
    mime_type: str | None = None
    file_size: int | None = None


class Video(BaseModel):
    file_id: str| None = None
    file_unique_id: str| None = None
    width: int| None = None
    height: int| None = None
    duration: int| None = None
    file_name: str | None = None
    mime_type: str | None = None
    file_size: int | None = None


class Voice(BaseModel):
    file_id: str| None = None
    file_unique_id: str| None = None
    duration: int| None = None
    mime_type: str | None = None
    file_size: int | None = None


class Audio(BaseModel):
    file_id: str| None = None
    file_unique_id: str| None = None
    duration: int| None = None
    performer: str | None = None
    title: str | None = None
    file_name: str | None = None
    mime_type: str | None = None
    file_size: int | None = None


class Animation(BaseModel):
    file_id: str| None = None
    file_unique_id: str| None = None
    width: int| None = None
    height: int| None = None
    duration: int| None = None
    file_name: str | None = None
    mime_type: str | None = None
    file_size: int | None = None
 
class FromUser(BaseModel):
    id: int| None = None
    is_bot: bool | None = None
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
    
class Message(BaseModel):

    # Cho phép dùng cả 'from_user' và 'from' khi khởi tạo
    model_config = ConfigDict(populate_by_name=True)

    chat: Chat | None = None 
    text: str | None = None  # Tin nhắn có thể là ảnh/sticker (không có text)
    caption: str | None = None  # Văn bản đi kèm media (ảnh/video/file)
    date: int | None = None 
    edit_date:int|None=None
    media_group_id: str | None = None
    photo: list[PhotoSize] | None = None
    document: Document | None = None
    video: Video | None = None
    voice: Voice | None = None
    audio: Audio | None = None
    animation: Animation | None = None
    entities:Any| None = None 
    link_preview_options:Any=None
    message_id:int | None = None 
    from_user: FromUser | None = Field(default=None, alias="from")
    reply_to_message: Optional['Message'] | None = None
    # class Config:
    #     # This allows you to populate the model using the alias "from" 
    #     # but also access it via "from_user"
    #     populate_by_name = True

class TelegramUpdate(BaseModel):
    update_id: int|None=None
    message: Message | None = None  # Có thể là edited_message, nên để None
    edited_message: Message | None = None  # Có thể là edited_message, nên để None
    ok:bool|None=None
    result: Message | None = None  # Có thể là kết quả post reply lên group
    new_chat_members:Any|None=None
    def get_chat_id(self):
        if self.message:
            return self.message.chat.id
        elif self.edited_message:
            return self.edited_message.chat.id
        elif self.result:
            return self.result.chat.id
        return None
    
    def get_message_date(self):
        if self.message:
            return self.message.date
        elif self.edited_message:
            return self.edited_message.date
        elif self.result:
            return self.result.date
        return None

    
    def get_from_user(self)->FromUser|None:
        if self.message:
            return self.message.from_user
        elif self.edited_message:
            return self.edited_message.from_user
        elif self.result:
            return self.result.from_user
        return None

    def get_text(self):
        if self.message:
            return self.message.text
        elif self.edited_message:
            return self.edited_message.text
        elif self.result:
            return self.result.text
        return None

    def get_users_mention(self):
        try:
            text_utf16 = (self.get_text()or"").encode('utf-16-le')
            users=[]
            if self.message.entities:
                for entity in self.message.entities:

                    username = ""   

                    if str(entity["type"]).lower() == "mention":
                        off = entity['offset'] * 2 # Nhân 2 vì mỗi unit trong utf-16-le là 2 bytes
                        ln = entity['length'] * 2
                        
                        # Cắt byte sau đó decode lại thành string
                        username = text_utf16[off : off + ln].decode('utf-16-le')
                        users.append({
                            "id":None,
                            "username": username.replace("@","")
                        })

                        continue

                    if str(entity["type"]).lower() == "text_mention":
                        try:
                            username = entity["user"]["username"] or ""   
                        except:
                            pass
                        fullname = ""   
                        try:
                            fullname = entity["user"]["fullname"] or ""   
                        except:
                            pass
                        first_name = ""   
                        try:
                            first_name = entity["user"]["first_name"] or ""   
                        except:
                            pass
                        last_name = ""   
                        try:
                            last_name = entity["user"]["last_name"] or ""   
                        except:
                            pass
                        u = {
                            "id": entity["user"]["id"],
                            "username": username.replace("@",""),
                            "fullname": fullname,
                            "is_bot": entity["user"]["is_bot"],
                            "first_name":first_name,
                            "last_name":last_name
                        }
                        users.append(u)
        
            # fromuser= self.get_from_user()
            # user_id = fromuser.id if fromuser else None
            # first_name = fromuser.first_name if fromuser else None
            # last_name = fromuser.last_name if fromuser else None
            # is_bot = fromuser.is_bot if fromuser else None

            # return {
            #     "id": user_id,
            #     "username": username,
            #     "fullname": fullname,
            #     "is_bot": is_bot,
            #     "first_name": first_name,
            #     "last_name": last_name
            # }
            return users
        except :
            return []

        pass
    def get_user_mention(self):
        text=self.get_text()
        if not text:
            return None
        # Handle fullname after tên: or ten: or name:
        # Use (?i) for case-insensitive, and \s* for optional spaces
        fullname_match = re.search(r"(?i)(?:\s+tên|\s+ten|\s+name)\s*:\s*(.+)", text)
        fullname=None
        if not fullname_match: 
            idx2cham= text.find(":")
            if idx2cham > -1:
                fullname = text[idx2cham+1:].strip()
        else:
            fullname = fullname_match.group(1).strip()


        if not fullname or fullname=="":
            raise ValueError("Không tìm thấy tên, cần theo mẫu vd: @username tên: fullname here")
                    
        if self.message.entities:
            for entity in self.message.entities:
                if str(entity["type"]).lower() == "text_mention":
                    username = ""   
                    try:
                        username = entity["user"]["username"] or ""   
                    except:
                        pass
                    # fullname = entity["user"]["first_name"] + " " + entity["user"]["last_name"]
                    return {
                        "id": entity["user"]["id"],
                        "username": username,
                        "fullname": fullname,
                        "is_bot": entity["user"]["is_bot"],
                        "first_name": entity["user"]["first_name"],
                        "last_name": entity["user"]["last_name"]
                    }
        
        # Handle username in text (e.g., @badpaybad)
        username_match = re.search(r"@(\w+)", text)
        if not username_match:
            # raise ValueError("Không tìm thấy username thiếu @ vd @username tên: fullname here")

            fromuser= self.get_from_user()
            user_id = fromuser.id if fromuser else None
            first_name = fromuser.first_name if fromuser else None
            last_name = fromuser.last_name if fromuser else None
            is_bot = fromuser.is_bot if fromuser else None

            return {
                "id": user_id,
                "username": username,
                "fullname": fullname,
                "is_bot": is_bot,
                "first_name": first_name,
                "last_name": last_name
            }
            
        username = username_match.group(1)

        return {
            "id": None,
            "username": username,
            "fullname": fullname,
            "is_bot": None,
            "first_name": None,
            "last_name": None
        }


class OrchestrationMessage(BaseModel):
    message: TelegramUpdate|None=None
    msg_id:str|None=None
    files:List[str]|None=None
    text:str|None=None
    chat_id:str|None=None
    webhook_base_url:str|None=None
    files_type:List[str]|None=None

    
        