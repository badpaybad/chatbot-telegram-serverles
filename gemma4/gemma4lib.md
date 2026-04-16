cần tạo module gemma4lib để thực hiện giống thư viện 
    from google import genai
    from google.genai import types
xem một số hàm sử dụng google genai ở knowledgebase/orchestrationcontext.py , skills/cli/tool_call_cli.py , skills/jira/tool_call_jira.py
tham khảo hàm viết cho các api gemma4/yeucau.md , gemma4/program.py

cần viêt thành gemma4lib.py để các module khác có thể import và sử dụng tuân thủ các inteface theo google genai 
mục tiêu để khi import gemma4lib thay cho google genai thì không cần thay đổi code ở các module khác 