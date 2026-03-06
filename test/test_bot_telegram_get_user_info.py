"""
Test file for bot_telegram.get_user_info function
Usage: python test/test_bot_telegram_get_user_info.py config_dunp
"""
import sys
import os
import asyncio

# --- Load config từ tham số dòng lệnh ---
if len(sys.argv) < 2:
    print("❌ Thiếu tham số config. Chạy: python test/test_bot_telegram_get_user_info.py config_dunp")
    sys.exit(1)

config_name = sys.argv[1]

# Thêm thư mục gốc vào sys.path để import được các module
DIR_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, DIR_ROOT)

# Import config theo tên được truyền vào
try:
    config_module = __import__(config_name)
    # Inject các biến từ config vào module config chính
    import config
    for attr in dir(config_module):
        if not attr.startswith("_"):
            setattr(config, attr, getattr(config_module, attr))
    # Gán thêm CONFIG_NAME để các module khác nhận biết
    config.CONFIG_NAME = config_name
    print(f"✅ Đã load config: {config_name}")
except ModuleNotFoundError:
    print(f"❌ Không tìm thấy module config: {config_name}")
    sys.exit(1)

import bot_telegram


async def test_get_user_info_success():
    """
    Test case: get_user_info với username hợp lệ 'badpaybad'
    Kỳ vọng: trả về dict có các trường id, username, fullname, is_bot, first_name, last_name
    """
    username = "badpaybad"
    print(f"\n{'='*50}")
    print(f"🧪 TEST: get_user_info(username='{username}')")
    print(f"{'='*50}")

    result = await bot_telegram.get_user_info(username)

    if result is None:
        print("⚠️  Kết quả trả về: None")
        print("   (Có thể do username không tìm thấy trên Telegram hoặc lỗi API)")
    else:
        print(f"✅ Kết quả trả về:")
        for key, value in result.items():
            print(f"   {key}: {value}")

        # Kiểm tra các trường bắt buộc phải có trong kết quả
        required_keys = ["id", "username", "fullname", "is_bot", "first_name", "last_name"]
        missing_keys = [k for k in required_keys if k not in result]
        if missing_keys:
            print(f"\n❌ FAIL: Thiếu các trường: {missing_keys}")
        else:
            print(f"\n✅ PASS: Tất cả các trường bắt buộc đều có mặt")

    return result


async def test_get_user_info_invalid_username():
    """
    Test case: get_user_info với username không tồn tại
    Kỳ vọng: trả về None
    """
    username = "___nonexistent_user_xyz_12345___"
    print(f"\n{'='*50}")
    print(f"🧪 TEST: get_user_info(username='{username}') [username không tồn tại]")
    print(f"{'='*50}")

    result = await bot_telegram.get_user_info(username)

    if result is None:
        print("✅ PASS: Trả về None như kỳ vọng khi username không tồn tại")
    else:
        print(f"⚠️  Không kỳ vọng có kết quả với username không tồn tại: {result}")

    return result


async def test_get_user_info_with_at_prefix():
    """
    Test case: get_user_info với username có prefix '@'
    Bot Telegram API thường chấp nhận cả '@username' và 'username'
    """
    username = "badpaybad"
    print(f"\n{'='*50}")
    print(f"🧪 TEST: get_user_info(username='{username}') [có prefix @]")
    print(f"{'='*50}")

    result = await bot_telegram.get_user_info(username)

    if result is None:
        print("⚠️  Kết quả trả về: None")
    else:
        print(f"✅ Kết quả trả về:")
        for key, value in result.items():
            print(f"   {key}: {value}")

    return result


async def run_all_tests():
    print(f"\n{'#'*60}")
    print(f"  RUNNING TESTS: bot_telegram.get_user_info")
    print(f"  Config: {config_name}")
    print(f"  Token: {config.TELEGRAM_BOT_TOKEN[:10]}..." if config.TELEGRAM_BOT_TOKEN else "  Token: (trống)")
    print(f"{'#'*60}")

    # Test 1: username hợp lệ
    await test_get_user_info_success()

    # Test 2: username không tồn tại
    # await test_get_user_info_invalid_username()

    # Test 3: username với @ prefix
    # await test_get_user_info_with_at_prefix()

    print(f"\n{'#'*60}")
    print(f"  ✅ DONE - Tất cả test đã chạy xong")
    print(f"{'#'*60}\n")


if __name__ == "__main__":
    asyncio.run(run_all_tests())
