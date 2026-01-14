

from google import genai
from google.genai import types

from config import GEMINI_APIKEY, GEMINI_MODEL

# --- CẤU HÌNH ---

# System instruction for the summarization model
system_instruction = """
Bạn là một trợ lý hữu ích chuyên tóm tắt các cuộc trò chuyện.
Bạn sẽ nhận được một đoạn văn bản chứa các tin nhắn từ một cuộc trò chuyện nhóm.
Nhiệm vụ của bạn là cung cấp một bản tóm tắt ngắn gọn về các chủ đề chính và những điểm quan trọng đã được thảo luận.
Bản tóm tắt phải bằng tiếng Việt.
Tập trung vào những thông tin quan trọng nhất và bỏ qua những cuộc trò chuyện không liên quan.
"""
# Bắt đầu bản tóm tắt bằng "Tổng kết các nội dung chính:".
# Khởi tạo client cấp thấp với API Key của bạn
client = genai.Client(api_key=GEMINI_APIKEY)


# Khai báo công cụ Google Search
tools = [
    types.Tool(
        google_search=types.GoogleSearch()
        # google_search_retrieval=types.GoogleSearchRetrieval(
        #     dynamic_retrieval_config=types.DynamicRetrievalConfig(
        #         mode=types.DynamicRetrievalConfigMode.MODE_DYNAMIC,
        #         dynamic_threshold=0.6  # AI tự quyết định có tìm hay không
        #     )
        # )
    ),
]

# Cấu hình sinh nội dung
generation_config = types.GenerateContentConfig(
    temperature=0.2,  # Độ sáng tạo ít để tập trung nội dung chính
    system_instruction=system_instruction,
    tools=tools,
    # tool_config=types.ToolConfig(
    #     function_calling_config=types.FunctionCallingConfig(
    #         mode="AUTO"
    #     ),
    # ),
)


def gemini_summary(text_to_summarize: str):
    # Prepending the system instruction to the user prompt is a robust way
    full_prompt = f"Dưới đây là đoạn hội thoại:\n\n{text_to_summarize}"

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        config=generation_config,
        contents=full_prompt,
    )

    return response.text
