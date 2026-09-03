#!/usr/bin/env python3
"""
Pipeline tạo video 3D Hologram hoàn chỉnh cho Lớp Bé 4 - Mầm non Đống Đa:
1. Tổng hợp nhạc nền đại dương (Ocean Ambient & Chimes) và hòa âm cùng voice.mp3.
2. Render hoạt cảnh 3D Hologram Rùa Biển bơi lội, phát sáng, đổi sắc thái theo kịch bản.
3. Xuất video đơn góc (single_view.mp4).
4. Ghép thành video Hologram 4 mặt (kim tự tháp 45 độ) chuẩn Tablet (16:9) và iPad (4:3).
"""

import math
import os
import subprocess
import sys
import cv2
import numpy as np


BASE_DIR = "/work/a.i-assistant-chatbot-telegram-serverles/hologram-video"
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def generate_ocean_ambient_wav(output_wav_path, duration, sample_rate=44100):
    """
    Dùng numpy và wave (chuẩn Python) để tạo bản nhạc nền đại dương êm dịu:
    - Sóng biển dập dềnh (lọc dải tần số thấp với nhịp thở 0.2Hz)
    - Hòa âm êm dịu cung Đô Trưởng / Fa Trưởng (Fmaj7 / Cmaj7) tạo cảm giác sâu lắng, hy vọng
    """
    import wave

    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    
    # 1. Giả lập tiếng sóng biển (noise với bộ điều biến tần số thấp lượn sóng)
    noise = np.random.normal(0, 0.08, len(t))
    wave_envelope = 0.5 + 0.5 * np.sin(2 * np.pi * 0.18 * t) # Nhịp sóng 5.5 giây 1 chu kỳ
    ocean_waves = noise * wave_envelope

    # 2. Hợp âm du dương ấm áp (C major / F major: C3 130.8Hz, G3 196Hz, A3 220Hz, C4 261.6Hz, E4 329.6Hz)
    chord = (
        0.04 * np.sin(2 * np.pi * 130.81 * t) +
        0.03 * np.sin(2 * np.pi * 196.00 * t) +
        0.03 * np.sin(2 * np.pi * 261.63 * t) +
        0.025 * np.sin(2 * np.pi * 329.63 * t)
    )
    # Thêm hiệu ứng tremolo nhẹ cho hợp âm
    chord = chord * (0.8 + 0.2 * np.sin(2 * np.pi * 0.5 * t))

    audio_signal = ocean_waves + chord

    # Fade in 2s, fade out 3s
    fade_in_len = int(sample_rate * 2.0)
    fade_out_len = int(sample_rate * 3.0)
    fade_in = np.linspace(0, 1, fade_in_len)
    fade_out = np.linspace(1, 0, fade_out_len)

    audio_signal[:fade_in_len] *= fade_in
    audio_signal[-fade_out_len:] *= fade_out

    # Giới hạn biên độ (clipping protection)
    audio_signal = np.clip(audio_signal, -0.95, 0.95)
    int16_audio = (audio_signal * 32767).astype(np.int16)

    # Xuất ra file WAV stereo (2 channels)
    stereo_audio = np.column_stack((int16_audio, int16_audio))

    with wave.open(output_wav_path, "w") as wav_file:
        wav_file.setnchannels(2)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(stereo_audio.tobytes())


def create_ambient_audio(voice_path, output_audio_path, total_duration):
    """
    Trộn giọng nói AI với nhạc nền đại dương vừa tổng hợp.
    """
    print("[1/4] Đang tổng hợp âm thanh (Voice + Ocean Ambient Music)...")
    temp_ambient_wav = os.path.join(OUTPUT_DIR, "ambient_ocean.wav")
    generate_ocean_ambient_wav(temp_ambient_wav, total_duration)

    cmd = [
        "ffmpeg", "-y",
        "-i", voice_path,
        "-i", temp_ambient_wav,
        "-filter_complex",
        f"""
        [0:a]adelay=2200|2200,volume=2.2[v];
        [1:a]volume=0.8[amb];
        [v][amb]amix=inputs=2:duration=longest:dropout_transition=2[mixed];
        [mixed]afade=t=in:ss=0:d=1.5,afade=t=out:st={total_duration-2.5}:d=2.5[aout]
        """,
        "-map", "[aout]",
        "-t", str(total_duration),
        "-c:a", "aac", "-b:a", "192k",
        output_audio_path
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if os.path.exists(temp_ambient_wav):
        os.remove(temp_ambient_wav)
    print(f"      -> Đã tạo file audio hoàn chỉnh: {output_audio_path}")


def render_single_view_video(audio_path, output_video_path, total_duration, fps=30, size=720):
    """
    Render video 1 góc nhìn độ phân giải 720x720:
    - Chú rùa biển phát sáng bơi lội với hiệu ứng uốn lượn (swimming float)
    - Khử hoàn toàn viền hộp đen (pure black thresholding + soft circular vignette)
    - Hạt bụi ánh sáng đại dương (bioluminescent floating particles)
    - Quá trình biến đổi màu sắc và tâm trạng theo timeline kịch bản
    """
    print(f"[2/4] Đang render hoạt cảnh 3D Hologram ({total_duration:.1f}s, {int(total_duration*fps)} frames)...")
    
    happy_img = cv2.imread(os.path.join(ASSETS_DIR, "turtle_happy.png"), cv2.IMREAD_UNCHANGED)
    sad_img = cv2.imread(os.path.join(ASSETS_DIR, "turtle_sad.png"), cv2.IMREAD_UNCHANGED)
    
    if happy_img.shape[2] == 4:
        happy_bgr = happy_img[:, :, :3]
    else:
        happy_bgr = happy_img
        
    if sad_img.shape[2] == 4:
        sad_bgr = sad_img[:, :, :3]
    else:
        sad_bgr = sad_img

    happy_bgr = cv2.resize(happy_bgr, (size, size), interpolation=cv2.INTER_AREA)
    sad_bgr = cv2.resize(sad_bgr, (size, size), interpolation=cv2.INTER_AREA)

    # 1. Tạo mặt nạ khử nhiễu viền (Circular Soft Vignette Mask)
    # Bán kính từ tâm, mờ dần từ 80% đến 95% bán kính
    Y, X = np.ogrid[:size, :size]
    dist_from_center = np.sqrt((X - size / 2.0) ** 2 + (Y - size / 2.0) ** 2)
    max_r = size * 0.46
    vignette = np.clip((max_r - dist_from_center) / (size * 0.08), 0.0, 1.0)
    vignette = (vignette * vignette * (3 - 2 * vignette)) # Smoothstep

    def clean_black_background(img):
        # Loại bỏ các pixel màu đen xám nhiễu (< 16)
        cleaned = img.copy()
        mask_low = np.max(cleaned, axis=2) < 16
        cleaned[mask_low] = [0, 0, 0]
        # Nhân với vignette để triệt tiêu hoàn toàn viền ảnh
        cleaned = (cleaned.astype(np.float32) * vignette[:, :, None]).astype(np.uint8)
        return cleaned

    happy_bgr = clean_black_background(happy_bgr)
    sad_bgr = clean_black_background(sad_bgr)

    total_frames = int(total_duration * fps)

    # Khởi tạo hạt ánh sáng sinh học (particles)
    np.random.seed(42)
    particles = []
    for _ in range(65):
        particles.append({
            "x": np.random.uniform(30, size - 30),
            "y": np.random.uniform(30, size - 30),
            "radius": np.random.uniform(1.2, 3.0),
            "speed_y": np.random.uniform(-0.8, -0.2),
            "speed_x": np.random.uniform(-0.3, 0.3),
            "phase": np.random.uniform(0, 2 * math.pi),
            "color": [int(np.random.uniform(210, 255)), int(np.random.uniform(220, 255)), int(np.random.uniform(0, 80))]
        })

    temp_raw_video = os.path.join(OUTPUT_DIR, "temp_render.mp4")
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(temp_raw_video, fourcc, fps, (size, size))

    center_x, center_y = size / 2.0, size / 2.0

    for f in range(total_frames):
        t = f / fps

        # Khung nền đen kịt tuyệt đối
        frame = np.zeros((size, size, 3), dtype=np.uint8)

        # Trọng số hòa trộn giữa Happy và Sad
        if t < 17.0:
            sad_weight = 0.0
        elif 17.0 <= t < 21.0:
            sad_weight = (t - 17.0) / 4.0
        elif 21.0 <= t < 28.0:
            sad_weight = 1.0
        elif 28.0 <= t < 31.0:
            sad_weight = 1.0 - (t - 28.0) / 3.0
        else:
            sad_weight = 0.0

        if sad_weight == 0.0:
            base_turtle = happy_bgr.copy()
        elif sad_weight == 1.0:
            base_turtle = sad_bgr.copy()
        else:
            base_turtle = cv2.addWeighted(happy_bgr, 1.0 - sad_weight, sad_bgr, sad_weight, 0)

        # Chuyển động bơi lượn 3D
        bob_y = math.sin(t * 1.5) * 12.0
        bob_x = math.cos(t * 0.8) * 6.0
        tilt_angle = math.sin(t * 1.2) * 2.5
        # Scale chuẩn 0.82 để nhân vật vừa vặn, không chạm viền
        scale_pulse = 0.82 * (1.0 + math.sin(t * 1.8) * 0.02)

        global_alpha = 1.0
        if t < 2.5:
            global_alpha = t / 2.5
            scale_pulse *= (0.75 + 0.25 * global_alpha)
        elif t > (total_duration - 3.0):
            global_alpha = max(0.0, (total_duration - t) / 3.0)
            scale_pulse *= (0.8 + 0.2 * global_alpha)

        # Biến đổi hình học
        M = cv2.getRotationMatrix2D((center_x, center_y), tilt_angle, scale_pulse)
        M[0, 2] += bob_x
        M[1, 2] += bob_y

        transformed_turtle = cv2.warpAffine(base_turtle, M, (size, size), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))

        if global_alpha < 1.0:
            transformed_turtle = (transformed_turtle.astype(np.float32) * global_alpha).astype(np.uint8)

        # Hạt phát sáng
        for p in particles:
            p["y"] += p["speed_y"]
            p["x"] += p["speed_x"] + math.sin(t * 2.0 + p["phase"]) * 0.3
            if p["y"] < 15:
                p["y"] = size - 20
                p["x"] = np.random.uniform(30, size - 30)

            sparkle_intensity = 0.5 + 0.5 * math.sin(t * 3.0 + p["phase"])
            p_color = [int(c * sparkle_intensity * global_alpha) for c in p["color"]]
            cv2.circle(frame, (int(p["x"]), int(p["y"])), int(p["radius"]), p_color, -1)

        # Cộng ánh sáng
        frame = cv2.add(frame, transformed_turtle)

        # Quét tia Hologram nhẹ
        scan_y = int((t * 120) % size)
        scan_thickness = 16
        if 0 <= scan_y < size:
            y1 = max(0, scan_y - scan_thickness)
            y2 = min(size, scan_y + scan_thickness)
            scan_strip = frame[y1:y2, :].astype(np.float32)
            frame[y1:y2, :] = np.clip(scan_strip * 1.08, 0, 255).astype(np.uint8)

        out.write(frame)

    out.release()

    # Ghép temp video với file audio đã tạo thành single_view.mp4
    cmd = [
        "ffmpeg", "-y",
        "-i", temp_raw_video,
        "-i", audio_path,
        "-c:v", "libx264", "-crf", "18", "-preset", "fast",
        "-c:a", "copy",
        "-shortest",
        output_video_path
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if os.path.exists(temp_raw_video):
        os.remove(temp_raw_video)
    print(f"      -> Đã xuất video đơn góc: {output_video_path}")


def render_4way_hologram_opencv(single_video_path, audio_path, output_tablet_16_9, output_ipad_4_3):
    """
    Ghép 4 hướng đối xứng qua tâm trực tiếp bằng OpenCV (không gian màu BGR chuẩn).
    Đảm bảo 100% nền đen tuyệt đối (0, 0, 0), triệt tiêu hoàn toàn lỗi lệch màu YUV.
    """
    print("[3/4] Đang dựng video Hologram 4 mặt Tablet 16:9 (1920x1080) bằng OpenCV...")
    cap = cv2.VideoCapture(single_video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Tablet 16:9 setup
    w_16_9, h_16_9 = 1920, 1080
    sub_16_9 = 420
    gap_16_9 = 65
    cx_16_9, cy_16_9 = w_16_9 // 2, h_16_9 // 2

    # iPad 4:3 setup
    w_4_3, h_4_3 = 2048, 1536
    sub_4_3 = 580
    gap_4_3 = 90
    cx_4_3, cy_4_3 = w_4_3 // 2, h_4_3 // 2

    temp_16_9 = os.path.join(OUTPUT_DIR, "temp_16_9.mp4")
    temp_4_3 = os.path.join(OUTPUT_DIR, "temp_4_3.mp4")

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out_16_9 = cv2.VideoWriter(temp_16_9, fourcc, fps, (w_16_9, h_16_9))
    out_4_3 = cv2.VideoWriter(temp_4_3, fourcc, fps, (w_4_3, h_4_3))

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # 1. Tạo 4 hướng cho Tablet 16:9
        f_sub_16_9 = cv2.resize(frame, (sub_16_9, sub_16_9), interpolation=cv2.INTER_AREA)
        f_bot_16_9 = f_sub_16_9 # 0 deg
        f_top_16_9 = cv2.rotate(f_sub_16_9, cv2.ROTATE_180) # 180 deg
        f_left_16_9 = cv2.rotate(f_sub_16_9, cv2.ROTATE_90_CLOCKWISE) # 90 deg
        f_right_16_9 = cv2.rotate(f_sub_16_9, cv2.ROTATE_90_COUNTERCLOCKWISE) # 270 deg

        canvas_16_9 = np.zeros((h_16_9, w_16_9, 3), dtype=np.uint8)

        # Bottom
        bx = cx_16_9 - sub_16_9 // 2
        by = cy_16_9 + gap_16_9
        canvas_16_9[by:by+sub_16_9, bx:bx+sub_16_9] = cv2.add(canvas_16_9[by:by+sub_16_9, bx:bx+sub_16_9], f_bot_16_9)

        # Top
        tx = cx_16_9 - sub_16_9 // 2
        ty = cy_16_9 - gap_16_9 - sub_16_9
        canvas_16_9[ty:ty+sub_16_9, tx:tx+sub_16_9] = cv2.add(canvas_16_9[ty:ty+sub_16_9, tx:tx+sub_16_9], f_top_16_9)

        # Left
        lx = cx_16_9 - gap_16_9 - sub_16_9
        ly = cy_16_9 - sub_16_9 // 2
        canvas_16_9[ly:ly+sub_16_9, lx:lx+sub_16_9] = cv2.add(canvas_16_9[ly:ly+sub_16_9, lx:lx+sub_16_9], f_left_16_9)

        # Right
        rx = cx_16_9 + gap_16_9
        ry = cy_16_9 - sub_16_9 // 2
        canvas_16_9[ry:ry+sub_16_9, rx:rx+sub_16_9] = cv2.add(canvas_16_9[ry:ry+sub_16_9, rx:rx+sub_16_9], f_right_16_9)

        out_16_9.write(canvas_16_9)

        # 2. Tạo 4 hướng cho iPad 4:3
        f_sub_4_3 = cv2.resize(frame, (sub_4_3, sub_4_3), interpolation=cv2.INTER_AREA)
        f_bot_4_3 = f_sub_4_3
        f_top_4_3 = cv2.rotate(f_sub_4_3, cv2.ROTATE_180)
        f_left_4_3 = cv2.rotate(f_sub_4_3, cv2.ROTATE_90_CLOCKWISE)
        f_right_4_3 = cv2.rotate(f_sub_4_3, cv2.ROTATE_90_COUNTERCLOCKWISE)

        canvas_4_3 = np.zeros((h_4_3, w_4_3, 3), dtype=np.uint8)

        # Bottom
        bx4 = cx_4_3 - sub_4_3 // 2
        by4 = cy_4_3 + gap_4_3
        canvas_4_3[by4:by4+sub_4_3, bx4:bx4+sub_4_3] = cv2.add(canvas_4_3[by4:by4+sub_4_3, bx4:bx4+sub_4_3], f_bot_4_3)

        # Top
        tx4 = cx_4_3 - sub_4_3 // 2
        ty4 = cy_4_3 - gap_4_3 - sub_4_3
        canvas_4_3[ty4:ty4+sub_4_3, tx4:tx4+sub_4_3] = cv2.add(canvas_4_3[ty4:ty4+sub_4_3, tx4:tx4+sub_4_3], f_top_4_3)

        # Left
        lx4 = cx_4_3 - gap_4_3 - sub_4_3
        ly4 = cy_4_3 - sub_4_3 // 2
        canvas_4_3[ly4:ly4+sub_4_3, lx4:lx4+sub_4_3] = cv2.add(canvas_4_3[ly4:ly4+sub_4_3, lx4:lx4+sub_4_3], f_left_4_3)

        # Right
        rx4 = cx_4_3 + gap_4_3
        ry4 = cy_4_3 - sub_4_3 // 2
        canvas_4_3[ry4:ry4+sub_4_3, rx4:rx4+sub_4_3] = cv2.add(canvas_4_3[ry4:ry4+sub_4_3, rx4:rx4+sub_4_3], f_right_4_3)

        out_4_3.write(canvas_4_3)

    cap.release()
    out_16_9.release()
    out_4_3.release()

    # Mux âm thanh với FFmpeg chuẩn H.264
    subprocess.run([
        "ffmpeg", "-y", "-i", temp_16_9, "-i", audio_path,
        "-c:v", "libx264", "-crf", "18", "-preset", "fast",
        "-c:a", "copy", "-shortest", output_tablet_16_9
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if os.path.exists(temp_16_9):
        os.remove(temp_16_9)
    print(f"      -> Video Tablet 16:9 hoàn tất: {output_tablet_16_9}")

    print("[4/4] Đang dựng video Hologram 4 mặt iPad Retina 4:3 (2048x1536)...")
    subprocess.run([
        "ffmpeg", "-y", "-i", temp_4_3, "-i", audio_path,
        "-c:v", "libx264", "-crf", "18", "-preset", "fast",
        "-c:a", "copy", "-shortest", output_ipad_4_3
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if os.path.exists(temp_4_3):
        os.remove(temp_4_3)
    print(f"      -> Video iPad 4:3 hoàn tất: {output_ipad_4_3}")


def main():
    voice_file = os.path.join(ASSETS_DIR, "voice.mp3")
    mixed_audio = os.path.join(OUTPUT_DIR, "soundtrack_mixed.aac")
    single_video = os.path.join(OUTPUT_DIR, "hologram_single_view.mp4")
    tablet_video = os.path.join(OUTPUT_DIR, "hologram_4way_tablet_16_9.mp4")
    ipad_video = os.path.join(OUTPUT_DIR, "hologram_4way_ipad_4_3.mp4")

    # Tính độ dài từ voice.mp3 + 4s đệm mở đầu và kết thúc
    # voice duration là 33.5s -> tổng video = 38.0s
    total_duration = 38.0

    print("=================================================================")
    print(" BẮT ĐẦU CHƯƠNG TRÌNH SINH VIDEO 3D HOLOGRAM CHO LỚP BÉ 4")
    print("=================================================================")
    
    create_ambient_audio(voice_file, mixed_audio, total_duration)
    render_single_view_video(mixed_audio, single_video, total_duration, fps=30, size=720)
    render_4way_hologram_opencv(single_video, mixed_audio, tablet_video, ipad_video)

    print("=================================================================")
    print(" TẤT CẢ CÁC VIDEO ĐÃ ĐƯỢC XUẤT XUẤT SẮC TẠI THƯ MỤC OUTPUT:")
    print(f" 1. Video 1 hướng (Gốc 720x720):      {single_video}")
    print(f" 2. Video Hologram Tablet (16:9):     {tablet_video}")
    print(f" 3. Video Hologram iPad Retina (4:3): {ipad_video}")
    print("=================================================================")


if __name__ == "__main__":
    main()
