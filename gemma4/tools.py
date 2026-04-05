import json
import re
import os
import sys
import inspect
from typing import List, Dict, Any, Callable

# Import shared manager
from gemma4.manager import get_manager

# Import all constants from config.py
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)
from config import *

class Gemma4Tools:
    """
    Lớp xử lý việc ánh xạ yêu cầu người dùng sang các hàm/công cụ (Tool Call)
    với hệ thống chấm điểm (scoring). 
    Hỗ trợ đăng ký hàm động và trích xuất từ docstring.
    """

    def __init__(self, model_id: str = "google/gemma-4-e4b-it"):
        self.manager = get_manager(model_id)
        self.tools = []

    def add_tool(self, tool_def: Dict[str, Any]):
        """
        Đăng ký một định nghĩa hàm thủ công.
        """
        if tool_def not in self.tools:
            self.tools.append(tool_def)
            print(f"[+] Đã đăng ký tool: {tool_def.get('name')}")

    def add_tool_from_func(self, func: Callable):
        """
        Đọc mô tả hàm chuẩn của Python (docstring) và signature để tự động đăng ký tool.
        """
        try:
            name = func.__name__
            doc = inspect.getdoc(func) or "Không có mô tả."
            
            # Trích xuất tham số từ type hints và signature
            signature = inspect.signature(func)
            parameters = {}
            for param_name, param in signature.parameters.items():
                param_type = "string" # Mặc định
                if param.annotation != inspect.Parameter.empty:
                    # Chuyển đổi type hint sang string đơn giản
                    if hasattr(param.annotation, "__name__"):
                        param_type = param.annotation.__name__
                    else:
                        param_type = str(param.annotation)
                
                parameters[param_name] = param_type

            tool_def = {
                "name": name,
                "description": doc,
                "parameters": parameters
            }
            self.add_tool(tool_def)
        except Exception as e:
            print(f"[-] Lỗi khi trích xuất tool từ function {getattr(func, '__name__', 'unknown')}: {str(e)}")

    def match_tools(self, user_input: str, tools_definitions: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Dựa trên yêu cầu của người dùng và danh sách công cụ, trả về gợi ý kèm score.
        Nếu tools_definitions là None, sử dụng danh sách tool đã đăng ký trong self.tools.
        """
        # Sử dụng tool đã đăng ký nếu không truyền vào cụ thể
        tools_list = tools_definitions if tools_definitions is not None else self.tools
        
        if not tools_list:
            return [{"function_name": "none", "score": 0, "reason": "Không có tool nào được đăng ký."}]

        # Chuyển định nghĩa tool sang chuỗi JSON để gửi LLM
        tools_json = json.dumps(tools_list, indent=2, ensure_ascii=False)
        
        # System Instruction chi tiết để đảm bảo LLM hiểu cấu trúc trả về
        prompt = f"""
Bạn là chuyên gia phân tích mục đích (intent classification) và trích xuất tham số.
Dưới đây là danh sách các công cụ (tools/functions) mà bạn có thể sử dụng:
{tools_json}

Yêu cầu hiện tại của người dùng: "{user_input}"

Nhiệm vụ của bạn:
1. Đánh giá tất cả các công cụ xem cái nào phù hợp nhất với yêu cầu trên.
2. Với mỗi công cụ được đánh giá, hãy trả về 'score' từ 0.0 (không liên quan) đến 1.0 (hoàn toàn trùng khớp).
3. Trích xuất các tham số (parameters) nếu có thông tin trong câu nói của người dùng.
4. Bắt buộc trả về kết quả dưới dạng một DANH SÁCH JSON (array) theo định dạng mẫu:
[
  {{
    "function_name": "tên_hàm",
    "score": 0.95,
    "reason": "Lý do vì sao hàm này phù hợp bằng tiếng Việt",
    "parameters": {{ "tham_số": "giá_trị" }}
  }}
]

Lưu ý: Chỉ trả về JSON nguyên khối, không giải thích thêm, ngôn ngữ trả ra là Tiếng Việt.
"""
        # Gọi LLM qua manager
        raw_response = self.manager.generate(prompt, max_tokens=1024)
        
        # Tìm và trích xuất khối JSON
        try:
            match = re.search(r"(\[.*\])", raw_response, re.DOTALL)
            if not match:
                match = re.search(r"(\{.*\})", raw_response, re.DOTALL)

            if match:
                result_data = json.loads(match.group(0))
                if isinstance(result_data, dict):
                    result_data = [result_data]
                
                result_data.sort(key=lambda x: x.get('score', 0), reverse=True)
                return result_data
            else:
                return [{"function_name": "unknown", "score": 0, "reason": "Không phân tích được JSON"}]
                
        except Exception as e:
            return [{"function_name": "error", "score": 0, "reason": f"Lỗi hệ thống: {str(e)}"}]

def match_tools(user_input: str, tools_definitions: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Hàm helper để gọi nhanh."""
    engine = Gemma4Tools()
    return engine.match_tools(user_input, tools_definitions)

if __name__ == "__main__":
    # Test case mẫu: đăng ký từ function
    def tra_cuu_lich_tau(ga_di: str, ga_den: str):
        """
        Tra cứu lịch trình tàu hỏa giữa hai ga cụ thể.
        """
        pass

    gtool = Gemma4Tools()
    gtool.add_tool_from_func(tra_cuu_lich_tau)
    
    query = "Tôi muốn đi từ Hà Nội đến Đà Nẵng bằng tàu hỏa vào ngày mai."
    print(f"[*] Đang phân tích: {query}")
    results = gtool.match_tools(query)
    print(json.dumps(results, indent=2, ensure_ascii=False))
