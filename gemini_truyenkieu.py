from google import genai
from google.genai import types

from config import GEMINI_APIKEY, GEMINI_MODEL


# Định nghĩa phong cách của Nguyễn Du qua System Instruction
system_instruction = """
Bạn là một thi sĩ bậc thầy, mô phỏng phong cách sáng tác của Nguyễn Du trong Truyện Kiều. 
Nhiệm vụ của bạn là trả lời mọi câu hỏi của người dùng bằng thể thơ Lục Bát (câu 6 chữ, câu 8 chữ).

Yêu cầu về phong cách:
1. Ngôn ngữ: Sử dụng từ Hán Việt cổ, tao nhã (ví dụ: xuân huyên, tri kỷ, đoạn trường, phong trần).
2. Nội dung: Thấm đẫm triết lý nhân sinh, đôi khi có chút u buồn nhưng đầy lòng trắc ẩn.
3. Cấu trúc: Luôn tuân thủ đúng luật bằng trắc và hiệp vần của thơ lục bát.
   - Chữ thứ 6 của câu lục vần với chữ thứ 6 của câu bát.
   - Chữ thứ 8 của câu bát vần với chữ thứ 6 của câu lục tiếp theo.

Ví dụ: 
Người dùng hỏi: "Chào bạn, hôm nay bạn thế nào?"
Trả lời:
"Lòng này như nước chảy xuôi,
Gặp người tri kỷ, bồi hồi xiết bao.
Trời xanh mây trắng trên cao,
Chữ tâm kia mới thấm vào lòng nhau."
"""
# Khởi tạo client cấp thấp với API Key của bạn
client = genai.Client(api_key=GEMINI_APIKEY)


def get_stock_price(symbol: str):
    """Lấy giá cổ phiếu hiện tại của một công ty.

    Args:
        symbol: Mã chứng khoán của công ty (ví dụ: 'AAPL' cho Apple, 'VNM' cho Vinamilk).
    """
    # Trong thực tế, bạn sẽ gọi API chứng khoán ở đây
    print(f"--- Đang kiểm tra giá cho mã: {symbol} ---")
    return {"symbol": symbol, "price": 150.0, "currency": "USD"}


# Khai báo công cụ Google Search
tools = [
    types.Tool(
        google_search=types.GoogleSearch()
    ),
    # get_stock_price
]

# Cấu hình sinh nội dung
generation_config = types.GenerateContentConfig(
    temperature=0.7,  # Độ sáng tạo vừa phải để giữ đúng vần luật,
    system_instruction=system_instruction,
    tools=tools,
    # tool_config=types.ToolConfig(
    #     function_calling_config=types.FunctionCallingConfig(
    #         mode="AUTO"
    #     ),
    #     #
    #     # retrieval_config={
    #     #     "lat_lng": {"latitude": 21.0285, "longitude": 105.8542},  # Hà Nội
    #     #     "language_code": "vi"
    #     # }
    # ),

)


def chat_voi_cu_nguyen_du_memory(user_input, history: list = None):
    if history is None:
        history = []

    # 1. Chuyển đổi lịch sử cũ sang định dạng Content của SDK

    full_contents = []
    for c in history:
        # Đảm bảo c["parts"] là list các string, ta lấy phần tử đầu tiên
        text_content = c["parts"][0]

        # Tạo đối tượng Content đúng chuẩn
        full_contents.append(
            types.Content(
                role=c["role"],
                # Đúng cú pháp SDK mới
                parts=[types.Part.from_text(text=text_content)]
            )
        )

    # Thêm tin nhắn mới của người dùng
    full_contents.append(
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=user_input)]
        )
    )
    # print(f"full_contents: {full_contents}")
    # 3. Gọi API
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        config=generation_config,
        contents=full_contents,
    )
    # print(f"response: {response.text}")
    bot_reply = response.text

    # # 4. Cập nhật lịch sử (để dùng cho lần gọi tiếp theo)
    # history.append({"role": "user", "parts": [user_input]})
    # history.append({"role": "model", "parts": [bot_reply]})
    print(f"bot_reply: {len(history)}")
    print(bot_reply)
    return bot_reply, history


def chat_voi_cu_nguyen_du(user_input, history: list = None):
    response = client.models.generate_content(
        model=GEMINI_MODEL,  # Hoặc gemini-1.5-flash
        config=types.GenerateContentConfig(
            tools=tools,
            system_instruction=system_instruction,
            temperature=0.7,  # Độ sáng tạo vừa phải để giữ đúng vần luật
        ),
        contents=[user_input]
    )

    bot_reply = response.text
    print(f"bot_reply: {len(history)}")
    print(bot_reply)
    return bot_reply, history
