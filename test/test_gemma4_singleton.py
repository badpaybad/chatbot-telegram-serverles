import sys
import os
import time
import threading
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest
from gemma4.manager import get_manager

class TestGemma4Singleton(unittest.TestCase):
    """
    Kiểm tra tính chất Singleton của Gemma4Manager.
    """

    def test_singleton_identity(self):
        # Lần gọi đầu tiên
        print("\n[*] Lần gọi get_manager(1)...")
        m1 = get_manager()
        
        # Lần gọi thứ hai
        print("[*] Lần gọi get_manager(2)...")
        m2 = get_manager()
        
        # Kiểm tra ID của object
        print(f"[i] ID instance 1: {id(m1)}")
        print(f"[i] ID instance 2: {id(m2)}")
        
        self.assertEqual(id(m1), id(m2), "Hai lần gọi get_manager phải trả về cùng một instance!")
        print("[+] Xác nhận: identity MATCH.")

    def test_singleton_thread_safety(self):
        instances = []
        
        def call_manager():
            m = get_manager()
            instances.append(m)

        # Chạy đồng thời 5 luồng cùng lúc gọi get_manager
        print(f"\n[*] Đang chạy 5 luồng gọi get_manager đồng thời...")
        threads = []
        for i in range(5):
            t = threading.Thread(target=call_manager)
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
            
        # Kiểm tra xem tất cả các instance có giống nhau không
        first_id = id(instances[0])
        for inst in instances[1:]:
            self.assertEqual(id(inst), first_id, "Thread safety failed: Multiple instances created!")
        
        print(f"[+] Xác nhận: {len(instances)} luồng đều nhận lại cùng 1 instance duy nhất.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.argv.append("config_dunp")
    
    if len(sys.argv) > 1 and (sys.argv[1] == "config_dunp" or sys.argv[1] == "config_ngoc"):
        config_name = sys.argv.pop(1)
        print(f"[*] Đang thực thi {os.path.basename(__file__)} với {config_name}...")
        
    unittest.main()
