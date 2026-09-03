#!/usr/bin/env python3
"""
Tự động ghép video 1 góc thành video 3D Hologram 4 mặt (kim tự tháp 45 độ) cho Tablet.
Sử dụng FFmpeg để căn chỉnh chính xác đối xứng 4 hướng (Trên, Dưới, Trái, Phải).

Cách dùng:
    python generate_hologram.py --input input_video.mp4 --output hologram_4way.mp4
    python generate_hologram.py --input input_video.mp4 --aspect tablet_16_9
    python generate_hologram.py --input input_video.mp4 --aspect ipad_4_3
"""

import argparse
import os
import shutil
import subprocess
import sys


def check_ffmpeg():
    if shutil.which("ffmpeg") is None:
        print("[LỖI] Không tìm thấy công cụ ffmpeg trên hệ thống.")
        print("Vui lòng cài đặt ffmpeg: sudo apt install -y ffmpeg")
        sys.exit(1)


def generate_hologram(input_file, output_file, aspect="16:9", size=480, dead_zone_gap=80):
    """
    aspect:
      - 16:9: canvas 1920x1080 (phổ biến trên tablet Android, iPad ngang)
      - 4:3 : canvas 2048x1536 (iPad chuẩn)
      - 1:1 : canvas 1080x1080 (hình vuông)
    """
    if not os.path.exists(input_file):
        print(f"[LỖI] File đầu vào không tồn tại: {input_file}")
        sys.exit(1)

    canvas_resolutions = {
        "16:9": (1920, 1080),
        "4:3": (2048, 1536),
        "1:1": (1080, 1080),
    }

    width, height = canvas_resolutions.get(aspect, (1920, 1080))

    print(f"[*] Bắt đầu xử lý video: {input_file}")
    print(f"[*] Canvas đích: {width}x{height} (tỷ lệ {aspect})")
    print(f"[*] Kích thước mỗi khung hình 3D: {size}x{size}px")

    # Filter complex FFmpeg
    # 1. Scale video gốc thành vuông (size x size)
    # 2. Nhân thành 4 luồng và xoay tương ứng:
    #    - Bottom: 0 deg
    #    - Top: 180 deg (PI)
    #    - Left: 90 deg (PI/2)
    #    - Right: 270 deg (3*PI/2)
    # 3. Tạo canvas đen và đặt 4 video đối xứng qua tâm
    
    # Tính toán tọa độ đặt:
    # Tâm canvas: (width/2, height/2)
    # Top: x = (width - size)/2, y = (height/2) - dead_zone_gap - size
    # Bottom: x = (width - size)/2, y = (height/2) + dead_zone_gap
    # Left: x = (width/2) - dead_zone_gap - size, y = (height - size)/2
    # Right: x = (width/2) + dead_zone_gap, y = (height - size)/2

    top_y = f"(H/2)-{dead_zone_gap}-{size}"
    bot_y = f"(H/2)+{dead_zone_gap}"
    left_x = f"(W/2)-{dead_zone_gap}-{size}"
    right_x = f"(W/2)+{dead_zone_gap}"

    filter_complex = f"""
    [0:v]scale={size}:{size}:force_original_aspect_ratio=decrease,pad={size}:{size}:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1[v_scaled];
    [v_scaled]split=4[v_bot][v_top_raw][v_left_raw][v_right_raw];
    [v_top_raw]rotate=PI:ow={size}:oh={size}[v_top];
    [v_left_raw]rotate=PI/2:ow={size}:oh={size}[v_left];
    [v_right_raw]rotate=3*PI/2:ow={size}:oh={size}[v_right];
    color=c=black:s={width}x{height}[bg];
    [bg][v_bot]overlay=x=(W-{size})/2:y={bot_y}[bg1];
    [bg1][v_top]overlay=x=(W-{size})/2:y={top_y}[bg2];
    [bg2][v_left]overlay=x={left_x}:y=(H-{size})/2[bg3];
    [bg3][v_right]overlay=x={right_x}:y=(H-{size})/2[outv]
    """.strip()

    cmd = [
        "ffmpeg",
        "-y",
        "-i", input_file,
        "-filter_complex", filter_complex,
        "-map", "[outv]",
        "-map", "0:a?",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        output_file
    ]

    print("[*] Đang thực thi FFmpeg...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print("[LỖI] Quá trình chuyển đổi thất bại:")
        print(result.stderr)
        sys.exit(1)

    print(f"[THÀNH CÔNG] Đã tạo video Hologram 4 mặt tại: {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Tạo video Hologram 4 mặt 3D cho tablet.")
    parser.add_argument("--input", "-i", required=True, help="Đường dẫn file video đơn đầu vào")
    parser.add_argument("--output", "-o", default="hologram_4way.mp4", help="Đường dẫn file video hologram 4 mặt đầu ra")
    parser.add_argument("--aspect", choices=["16:9", "4:3", "1:1"], default="16:9", help="Tỷ lệ màn hình tablet (16:9, 4:3, 1:1)")
    parser.add_argument("--size", type=int, default=450, help="Kích thước mỗi góc hình (mặc định: 450px)")
    parser.add_argument("--gap", type=int, default=60, help="Khoảng cách từ tâm đến các khung hình (mặc định: 60px)")

    args = parser.parse_args()
    check_ffmpeg()
    generate_hologram(args.input, args.output, args.aspect, args.size, args.gap)


if __name__ == "__main__":
    main()
