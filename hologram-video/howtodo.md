# Hướng Dẫn Chi Tiết Sản Xuất Video 3D Hologram 4 Mặt Cho Tablet (Dự Án Mầm Non Đống Đa - Lớp Bé 4)

Tài liệu này cung cấp quy trình hoàn chỉnh từ A-Z để sản xuất **video 3D Hologram 4 mặt (kim tự tháp nghiêng 45 độ)** trình chiếu trên máy tính bảng (iPad / Android Tablet), phục vụ bài học giáo dục môi trường biển cho các bé lớp Bé 4, Trường Mầm non Đống Đa.

---

## 1. Nguyên Lý Kỹ Thuật Hologram Kim Tự Tháp 4 Mặt (Pepper's Ghost 3D)

### 1.1. Cơ chế phản xạ quang học 45°
* **Nguyên lý Pepper's Ghost**: Hình ảnh hiển thị trên màn hình phẳng nằm ngang (tablet) phát ra ánh sáng; khi gặp mặt kính/mica trong suốt đặt nghiêng đúng một góc **45 độ**, chùm sáng bị phản chiếu 90 độ lên mắt người xem. Do tấm mica trong suốt, mắt vừa nhìn thấy hình ảnh phản chiếu lơ lửng bên trong lòng tháp, vừa nhìn xuyên qua hậu cảnh phía sau, tạo ảo giác **vật thể 3D thực sự đang trôi nổi trong không trung**.
* **Đặc tính 4 mặt**: Khi bố trí 4 mặt mica chụm lại hình kim tự tháp cụt, cả 4 hướng (Đông, Tây, Nam, Bắc) đều nhìn thấy nhân vật 3D cùng lúc, giúp các bé mầm non có thể ngồi quây quần tròn quanh bàn học để cùng quan sát.

```
       [Đáy tháp mở / Mắt bé nhìn vào]
              \               /
               \  [ẢO ẢNH 3D] /  <-- Nghiêng 45 độ
                \     ⭐     /
          -------+---------+-------   <-- Màn hình Tablet (Nằm ngang)
                 [Màn hình Tablet]
```

### 1.2. Quy tắc bắt buộc của Video Hologram
1. **Nền đen tuyệt đối (True Black - #000000 / RGB 0, 0, 0)**:
   * Trên màn hình tablet (đặc biệt là màn OLED/AMOLED hoặc IPS có độ tương phản cao), màu đen không phát sáng (pixel tắt hoặc phát sáng rất thấp). Nhờ đó, khung viền video biến mất hoàn toàn, chỉ có nhân vật phát sáng được phản chiếu lên kính.
2. **Bố cục 4 hướng đối xứng (4-Way Cross Layout)**:
   * Màn hình chia thành 4 phân vùng: **Trên (Top)**, **Dưới (Bottom)**, **Trái (Left)**, **Phải (Right)**.
   * Tâm màn hình chừa một khoảng trống hình vuông (vùng chết - Dead Zone) đúng bằng kích thước đỉnh kim tự tháp úp xuống.
   * **Chiều xoay (Orientation)**:
     * Video **Dưới (Bottom)**: Góc 0° (đầu nhân vật hướng vào tâm tháp).
     * Video **Trên (Top)**: Xoay 180° (đầu nhân vật hướng vào tâm tháp).
     * Video **Trái (Left)**: Xoay 90° theo chiều kim đồng hồ (đầu hướng vào tâm).
     * Video **Phải (Right)**: Xoay 270° (ngược chiều kim đồng hồ 90°, đầu hướng vào tâm).
3. **Hiệu ứng thị giác (Aesthetics)**:
   * Nhân vật nên có hiệu ứng **phát sáng dạ quang (Bioluminescent / Neon Glow / Wireframe Hologram)** với tông màu xanh lam (Cyan `#00e5ff`), xanh ngọc biển (Aquamarine) hoặc vàng ánh kim để đạt độ tương phản mạnh nhất trên nền kính trong suốt.

---

## 2. Kịch Bản & Phân Cảnh Chi Tiết (Storyboard & Timeline 30s - 60s)

* **Nhân vật đại diện**: **Chú Rùa Biển Con Phát Sáng (Bioluminescent Baby Sea Turtle)** - đôi mắt to tròn, biểu cảm linh hoạt, thân thiện và gần gũi với lứa tuổi mầm non (3 - 4 tuổi).
* **Thời lượng chuẩn**: **55 giây**.
* **Ngôn ngữ**: Tiếng Việt (Giọng đọc AI ấm áp, truyền cảm, tốc độ chậm rãi).

### Bảng phân cảnh chi tiết (Storyboard):

| Thời gian | Hình ảnh nhân vật 3D Hologram | Âm thanh & Tiếng động (SFX) | Lời thoại (Voice-over) |
| :--- | :--- | :--- | :--- |
| **00:00 - 00:08** *(8s)* | Chú rùa biển phát sáng xanh biếc từ từ bơi từ phía xa tiến lại gần tâm, vẫy 2 vây trước chào các bé, chớp mắt thân thiện. | Tiếng bong bóng nước (`bubble sfx`), tiếng chuông gió ma thuật (`magic chime`). Nhạc nền piano êm dịu bắt đầu vang lên. | *"Xin chào các bạn nhỏ lớp Bé 4, Trường Mầm non Đống Đa!"* |
| **00:08 - 00:23** *(15s)* | Rùa biển tung tăng lượn một vòng cung mềm mại giữa làn nước phát sáng lung linh, vây lướt nhẹ, biểu cảm vui tươi hạnh phúc. | Tiếng sóng biển êm dịu rì rào (`gentle ocean wave`), đàn cá nhỏ phát sáng bơi thoáng qua. | *"Ngày xưa, tôi từng được tung tăng bơi lội giữa một đại dương xanh thẳm, trong lành..."* |
| **00:23 - 00:36** *(13s)* | Ánh sáng của rùa mờ dần chuyển sang xám nhạt và ánh đỏ cam cảnh báo. Xung quanh xuất hiện các mảnh túi nilon, chai nhựa trôi lập lờ. Rùa bơi chậm lại, co vây, ánh mắt đượm buồn. | Nhạc nền chùng xuống, có tiếng sột soạt nhẹ của túi nhựa và âm bass trầm cảnh báo nghẹt thở. | *"Nhưng còn bây giờ, tôi chỉ là một ký ức phát sáng giữa một vùng biển đang nghẹt thở vì rác thải nhựa và hơi nóng."* |
| **00:36 - 00:47** *(11s)* | Chú rùa tiến sát mặt kính, nghiêng đầu, 2 mắt long lanh như muốn chạm vào các bé qua tấm kính, thân hình chập chờn như tín hiệu hologram sắp tắt. | Hiệu ứng âm thanh glitch nhẹ kiểu hologram (`hologram hum/flicker`), tiếng violin da diết. | *"Nếu các bạn không chung tay bảo vệ và cứu lấy ngôi nhà đại dương của tôi, có lẽ sau này, tôi sẽ chỉ còn có thể tồn tại trong những hình ảnh chiếu lặp như thế này mà thôi..."* |
| **00:47 - 00:55** *(8s)* | Rùa biển bừng sáng trở lại màu xanh ngọc hy vọng rực rỡ, nở nụ cười tươi, vẫy vây chào tạm biệt các bé. | Nhạc nền dâng lên giai điệu tươi sáng, ấm áp, tiếng chuông ngân hy vọng. | *"Hãy chung tay bảo vệ môi trường sống nhé! Cảm ơn các bạn lớp Bé 4."* |
| **00:55 - 01:00** *(5s)* | Chú rùa bơi lùi dần vào tâm rồi tan biến thành hàng ngàn đốm sáng nhỏ li ti (hạt particle phát sáng) rồi tắt hẳn về màn hình đen. | Tiếng hạt sáng lấp lánh tan dần (`sparkle fade out`). | *(Nhạc fade out êm dịu)* |

---

## 3. Các Phương Pháp Tạo Video 3D Nền Đen (Video Asset Generation)

Để có được video 1 góc nhìn (Single View Video) làm nguồn, bạn có thể chọn 1 trong 3 phương pháp dưới đây:

### Phương pháp 1: Sử dụng AI Video Generator (Nhanh nhất, chất lượng cao, thẩm mỹ điện ảnh)

Sử dụng các công cụ Text-to-Video hoặc Image-to-Video AI như **Runway Gen-3**, **Kling AI**, **Luma Dream Machine**, hoặc **Haiper AI**.

#### Bước 1: Tạo hình ảnh nhân vật bằng Midjourney / Flux (Prompt mẫu)
```text
A cute 3D cartoon baby sea turtle swimming, glowing bioluminescent neon cyan and mint green lighting, translucent glass shell with glowing magical patterns, big expressive friendly eyes, swimming pose, isolated on pitch black pure black background (#000000), Octane Render, Unreal Engine 5 style, 8k resolution, cinematic lighting --ar 16:9 --no floor, seabed, coral, text, watermark
```

#### Bước 2: Tạo chuyển động video bằng Runway Gen-3 / Kling AI
* Đưa ảnh vừa tạo vào Runway Gen-3 (chế độ Image to Video) hoặc dùng Prompt trực tiếp:
```text
The glowing baby sea turtle swims slowly towards the camera, waving its front flippers gently in a friendly greeting, blinking its big expressive eyes, mouth smiling softly. Bioluminescent particles float around it. Seamless motion, isolated on pure black background. Camera remains static.
```

---

### Phương pháp 2: Sử dụng Blender 3D (Chủ động kiểm soát góc quay 100%)

Nếu có kỹ năng dựng 3D hoặc muốn render chuẩn 4 camera cùng lúc:
1. **Tìm Model 3D**: Tải miễn phí model chú rùa biển cartoon từ Sketchfab hoặc CGTrader (định dạng `.fbx` hoặc `.blend`).
2. **Tạo Shader Hologram**:
   * Trong Blender Shader Editor, gán cho model: `Principled BSDF` + `Emission Shader` (Color: `#00E5FF`, Strength: 3.0).
   * Thêm `Fresnel` node nối vào Emission để viền ngoài rực sáng hơn bên trong.
3. **Thiết lập World & Camera**:
   * World Background Color: Kéo thanh màu về **đen kịt tuyệt đối** `RGB (0, 0, 0)`.
   * Camera: Tiêu cự 50mm hoặc 85mm, góc nhìn chính diện.
4. **Render Output**:
   * Định dạng: MP4 (H.264) hoặc QuickTime PNG/ProRes.
   * Render ở độ phân giải 1080p, 30fps hoặc 60fps.

---

### Phương pháp 3: Tải Stock Footage 3D Hologram Sẵn Có

Nếu cần triển khai gấp trong ngày:
* Lên YouTube hoặc các trang stock (Pexels, Pixabay) tìm kiếm từ khóa:
  * `Hologram sea turtle black background 4k`
  * `Bioluminescent turtle black background 3d animation`
  * `Hologram whale 3d black screen`
* Tải video chất lượng 1080p hoặc 4K về để làm nguồn xử lý.

---

## 4. Hướng Dẫn Thu Âm & Lồng Tiếng AI (Voice-Over & Audio Design)

### 4.1. Tạo Voice AI Tiếng Việt chất lượng cao
Trẻ mầm non 3-4 tuổi phản ứng rất tốt với chất giọng ấm áp, trong trẻo như cô giáo mầm non hoặc giọng ngọt ngào của một người bạn hoạt hình:
1. **Nền tảng đề xuất**:
   * **ElevenLabs**: Sử dụng mô hình `Eleven Multilingual v2`, chọn giọng nữ trầm ấm hoặc giọng thiếu nhi.
   * **Vbee AIVoice / FPT.AI**: Chọn giọng đọc `Ngọc Mai` (Hà Nội, biểu cảm mầm non) hoặc `Chi Mai` (dịu dàng, truyền cảm).
   * **CapCut Voice Text**: Sử dụng giọng đọc *"Cô gái hoạt hình"* hoặc *"Nữ phát thanh viên"*.
2. **Thông số điều chỉnh**:
   * **Tốc độ (Speed)**: Giảm xuống **0.9x** hoặc **0.85x** để phát âm tròn vành rõ chữ, chậm rãi cho các bé nghe kịp.
   * **Ngắt nghỉ (Punctuation)**: Đặt dấu phẩy `,` và dấu ba chấm `...` đúng chỗ để tạo khoảng lặng lắng đọng khi nói về môi trường biển bị ô nhiễm.

### 4.2. Trộn âm thanh (Audio Mixing)
* **Voice Track**: Âm lượng +1 dB đến +2 dB (to, rõ, sáng).
* **Music Background**: Nhạc nền giao hưởng piano/string nhẹ nhàng, âm lượng duy trì ở mức `-18 dB` đến `-22 dB` để không át giọng nói. Khi giọng rùa nghẹn ngào, hạ nhỏ nhạc; đến đoạn hô vang khẩu hiệu *"Hãy chung tay bảo vệ môi trường..."*, đẩy nhạc lên `-14 dB`.
* **Sound Effects (SFX)**: Chèn đúng thời điểm rùa vẫy tay, bong bóng vỡ, và tiếng hạt phát sáng tan biến.

---

## 5. Ghép Video 4 Mặt Hologram (Hologram 4-Side Layout)

Sau khi có video đơn (1 góc nhìn) dài ~55s đã hòa trộn âm thanh hoàn chỉnh, ta tiến hành nhân bản thành bố cục 4 mặt cho tablet.

### 5.1. Sơ đồ bố cục khung hình Tablet

```
+-------------------------------------------------------------+
|                                                             |
|                         [TOP VIDEO]                         |
|                         (Xoay 180°)                         |
|                                                             |
|      [LEFT VIDEO]     +-------------+    [RIGHT VIDEO]      |
|       (Xoay 90°)      |  DEAD ZONE  |     (Xoay 270°)       |
|                       | (Tâm trống) |                       |
|                       +-------------+                       |
|                                                             |
|                        [BOTTOM VIDEO]                       |
|                          (Góc 0°)                           |
|                                                             |
+-------------------------------------------------------------+
                     Màn hình Tablet (16:9 / 4:3)
```

* **Vùng tâm (Dead Zone)**: Là hình vuông trống màu đen ở chính giữa màn hình (kích thước cạnh khoảng **15% - 20%** chiều rộng màn hình), tương ứng với phần đỉnh bằng của kim tự tháp mica.

---

### 5.2. Cách 1: Tự động hóa bằng FFmpeg (Chỉ 1 dòng lệnh - Siêu nhanh & Chính xác tuyệt đối)

FFmpeg là công cụ dòng lệnh mã nguồn mở mạnh mẽ nhất để dựng video 4 mặt đối xứng. Bạn không cần căn chỉnh thủ công bằng mắt.

Cài đặt FFmpeg (nếu chưa có):
```bash
sudo apt update && sudo apt install -y ffmpeg
```

#### Lệnh FFmpeg tạo video Hologram 4 mặt chuẩn 1920x1080 (hoặc 1080x1080 vuông):

Giả sử file gốc là `turtle_single.mp4`, lệnh sau sẽ tự động crop/scale, xoay 4 góc và ghép vào 1 canvas đen `1920x1080`:

```bash
ffmpeg -i turtle_single.mp4 -filter_complex "
  [0:v]scale=480:480,setsar=1[v_orig];
  [v_orig]split=4[v_bottom][v_top_raw][v_left_raw][v_right_raw];
  [v_top_raw]rotate=PI:ow=480:oh=480[v_top];
  [v_left_raw]rotate=PI/2:ow=480:oh=480[v_left];
  [v_right_raw]rotate=3*PI/2:ow=480:oh=480[v_right];
  color=c=black:s=1920x1080:d=60[bg];
  [bg][v_bottom]overlay=x=(W-w)/2:y=H-h-20[bg1];
  [bg1][v_top]overlay=x=(W-w)/2:y=20[bg2];
  [bg2][v_left]overlay=x=(W/2)-w-100:y=(H-h)/2[bg3];
  [bg3][v_right]overlay=x=(W/2)+100:y=(H-h)/2[outv]
" -map "[outv]" -map 0:a -c:v libx264 -crf 18 -preset fast -c:a aac -b:a 192k hologram_tablet_4way.mp4
```

> **Ghi chú**: Đã có sẵn file script Python `generate_hologram.py` trong thư mục `hologram-video/` để bạn có thể chạy chỉ bằng lệnh `python generate_hologram.py`.

---

### 5.3. Cách 2: Dựng thủ công bằng CapCut / Premiere Pro / After Effects

Nếu bạn muốn tùy biến trực quan bằng phần mềm dựng video:

#### Thao tác trên CapCut (PC hoặc Mobile):
1. **Tạo dự án mới**: Thiết lập tỉ lệ khung hình Canvas là **16:9** (hoặc **1:1** nếu dùng màn vuông). Nền Canvas chọn màu **Đen**.
2. **Kéo video đơn vào Track chính** (đây sẽ là video **Bottom**):
   * Thu nhỏ tỷ lệ còn khoảng **35% - 40%**.
   * Đặt ở chính giữa mép dưới màn hình. Góc quay giữ nguyên **0°**.
3. **Thêm Lớp phủ (Overlay) lần 1** (video **Top**):
   * Thêm lại video đơn đó vào lớp Overlay.
   * Thu nhỏ cùng tỷ lệ (35% - 40%).
   * Đặt ở chính giữa mép trên màn hình.
   * Xoay góc **180°** (đầu nhân vật chúc xuống hướng vào tâm).
4. **Thêm Lớp phủ (Overlay) lần 2** (video **Left**):
   * Thu nhỏ cùng tỷ lệ.
   * Đặt ở mép bên trái màn hình.
   * Xoay góc **90° theo chiều kim đồng hồ** (đầu nhân vật quay sang phải hướng vào tâm).
5. **Thêm Lớp phủ (Overlay) lần 3** (video **Right**):
   * Thu nhỏ cùng tỷ lệ.
   * Đặt ở mép bên phải màn hình.
   * Xoay góc **-90° hoặc 270°** (đầu nhân vật quay sang trái hướng vào tâm).
6. **Kiểm tra đồng bộ**: Tắt âm thanh của 3 track overlay, chỉ giữ lại âm thanh của 1 track chính để tránh bị vang vọng âm thanh.
7. **Xuất video**: Chọn độ phân giải **1080p** hoặc **2K/4K**, 60fps để chuyển động mượt mà.

---

## 6. Chế Tạo Kim Tự Tháp Hologram DIY Cho Máy Tính Bảng

Kim tự tháp 4 mặt có thể tự chế tạo dễ dàng bằng vật liệu tái chế hoặc đồ dùng văn phòng trong vòng 15 phút với chi phí dưới 30.000 VNĐ.

### 6.1. Chuẩn bị vật liệu & dụng cụ
* **Tấm vật liệu trong suốt**:
  * Tốt nhất: Tấm mica trong suốt (dày 0.8mm - 1mm) hoặc vỏ hộp nhựa dẻo trong (vỏ hộp đĩa CD/DVD cũ hoặc hộp đựng đồ chơi trong suốt).
  * Đơn giản nhất: Bìa bóng kính đóng sách A4 loại dày (bìa mica 0.2mm - 0.3mm mua tại mọi quán photocopy).
* **Dụng cụ**:
  * Dao rọc giấy / Kéo sắc.
  * Thước kẻ kim loại, bút dạ dầu để kẻ mẫu.
  * Băng keo trong suốt (loại siêu trong, bề rộng 1cm).

---

### 6.2. Kích thước cắt hình học chuẩn cho Tablet (Màn hình 10 - 11 inch như iPad / Galaxy Tab)

Kim tự tháp gồm **4 tấm hình thang cân giống hệt nhau**:

```
                 a = 2.0 cm (Đáy nhỏ)
               +-------------+
              /               \
             /                 \
     h = 8.5 cm               h = 8.5 cm (Chiều cao mặt nghiêng)
           /                     \
          /                       \
         +-------------------------+
             b = 12.0 cm (Đáy lớn)
```

* **Kích thước chi tiết**:
  * **Đáy nhỏ (a)**: `2.0 cm` (tiếp xúc với màn hình tablet).
  * **Đáy lớn (b)**: `12.0 cm` (hướng lên trên phía mắt người xem).
  * **Chiều cao mặt nghiêng (h)**: `8.5 cm` (tạo độ nghiêng chính xác xấp xỉ 45 độ so với mặt bàn).
  * *(Nếu dùng iPad lớn 12.9 inch: Nhân kích thước trên với hệ số 1.25 -> a=2.5cm, b=15cm, h=10.5cm)*.

---

### 6.3. Quy trình lắp ráp
1. **Bước 1 (Vẽ mẫu)**: Vẽ hình thang cân lên một tờ giấy trắng theo đúng kích thước trên.
2. **Bước 2 (Cắt vật liệu)**: Đặt tấm bóng kính/mica lên trên tờ giấy mẫu, dùng thước kẻ và dao rọc giấy cắt cẩn thận thành 4 hình thang rời (hoặc vẽ liền kề 4 hình rồi khía nhẹ nếp gấp để không phải dán nhiều).
3. **Bước 3 (Dán liên kết)**:
   * Xếp 4 cạnh bên của 4 hình thang nằm sát nhau trên mặt bàn phẳng.
   * Dán băng dính trong suốt dọc theo 3 mép tiếp giáp giữa các mặt.
   * Nhấc lên, gấp 4 mặt lại thành hình chóp cụt kim tự tháp, sau đó dán mép tiếp giáp cuối cùng lại.
4. **Bước 4 (Cắt bớt keo thừa)**: Miết kỹ băng keo trong để không để lại bọt khí làm khúc xạ ánh sáng.

---

## 7. Quy Trình Vận Hành Trình Chiếu Tại Lớp Mầm Non Bé 4

Để buổi trình chiếu mang lại cảm xúc kỳ diệu và sự tập trung cao nhất cho các bé lớp Bé 4:

### 7.1. Chuẩn bị thiết bị và không gian
1. **Môi trường ánh sáng**:
   * Kéo rèm cửa sổ, tắt đèn trần trong phòng học. Ánh sáng càng tối, hình ảnh 3D hologram càng nổi rõ, rực rỡ và chân thực.
2. **Thiết lập Tablet**:
   * Tăng **độ sáng màn hình lên 100%**.
   * Tắt tính năng tự động khóa màn hình (`Auto-lock: Never`).
   * Đặt tablet nằm ngửa phẳng trên bàn tròn ở trung tâm lớp học.
   * Mở video ở chế độ **Lặp lại vô tận (Loop Video)** và toàn màn hình (Full Screen).
3. **Đặt tháp Hologram**:
   * Đặt kim tự tháp cụt lên chính giữa màn hình tablet: **Đáy nhỏ (2cm) úp xuống chạm vào mặt kính tablet**, ngay ngắn ở tâm vuông (Dead Zone). Đáy lớn hướng lên trần nhà.
   * Căn chỉnh sao cho 4 mặt kính hướng thẳng về phía 4 cụm video trên màn hình.

---

### 7.2. Kịch bản sư phạm kết hợp cùng cô giáo (5 - 7 phút)

1. **Giai đoạn 1: Tạo bất ngờ & Dẫn nhập (1 phút)**:
   * Cô giáo tập trung các bé lại quanh bàn tròn: *"Hôm nay cô có một chiếc hộp ánh sáng thần kỳ mang theo một người bạn đặc biệt từ đại dương xa xôi đến thăm lớp Bé 4 chúng mình đấy!"*
   * Bắt đầu bật video. Chú rùa biển 3D phát sáng bồng bềnh giữa lòng tháp xuất hiện.
2. **Giai đoạn 2: Lắng nghe tâm sự của Rùa Biển (1 phút)**:
   * Cho các bé đứng hoặc ngồi nhìn nghiêng vào các mặt kính (tầm mắt ngang với thành kính).
   * Lắng nghe trọn vẹn lời thoại và quan sát chuyển biến màu sắc của chú rùa khi đại dương bị ô nhiễm.
3. **Giai đoạn 3: Tương tác sư phạm & Cam kết hành động (3 - 5 phút)**:
   * Cô giáo đặt câu hỏi gợi mở:
     * *"Các con có thấy bạn rùa biển phát sáng đẹp không nào?"*
     * *"Tại sao vừa rồi bạn rùa lại buồn và đổi sang màu xám thế nhỉ?"*
     * *(Bé trả lời: Vì rác thải nhựa, vì biển bị bẩn ạ!)*
     * *"Vậy lớp Bé 4 chúng mình cần làm gì để cứu ngôi nhà của bạn rùa?"*
   * Cô giáo chốt lại thông điệp: Không vứt rác bừa bãi, bỏ rác vào thùng, tiết kiệm điện nước để bảo vệ hành tinh xanh.

---

## 8. Danh Sách File Công Cụ Bổ Trợ Đi Kèm

Trong thư mục `hologram-video/`:
* [whattodo.md](file:///work/a.i-assistant-chatbot-telegram-serverles/hologram-video/whattodo.md): Yêu cầu và kịch bản gốc.
* [howtodo.md](file:///work/a.i-assistant-chatbot-telegram-serverles/hologram-video/howtodo.md): Tài liệu hướng dẫn kỹ thuật chi tiết này.
* [render_hologram_show.py](file:///work/a.i-assistant-chatbot-telegram-serverles/hologram-video/render_hologram_show.py): Pipeline hoàn chỉnh từ sinh Voice AI + Nhạc đại dương + Hoạt cảnh 3D + Ghép 4 mặt Hologram.
* [generate_hologram.py](file:///work/a.i-assistant-chatbot-telegram-serverles/hologram-video/generate_hologram.py): Script Python tiện ích sinh video Hologram 4 mặt từ bất kỳ video đầu vào nào.

### Thành phẩm video xuất xưởng trong thư mục `output/`:
* **[hologram_4way_tablet_16_9.mp4](file:///work/a.i-assistant-chatbot-telegram-serverles/hologram-video/output/hologram_4way_tablet_16_9.mp4)**: Video chuẩn Full HD 1920x1080 dành cho máy tính bảng tỷ lệ 16:9 / 16:10.
* **[hologram_4way_ipad_4_3.mp4](file:///work/a.i-assistant-chatbot-telegram-serverles/hologram-video/output/hologram_4way_ipad_4_3.mp4)**: Video chuẩn Retina 2048x1536 dành cho iPad tỷ lệ 4:3.
* **[hologram_single_view.mp4](file:///work/a.i-assistant-chatbot-telegram-serverles/hologram-video/output/hologram_single_view.mp4)**: Video 1 hướng góc nhìn chính diện 720x720.
* **[soundtrack_mixed.aac](file:///work/a.i-assistant-chatbot-telegram-serverles/hologram-video/output/soundtrack_mixed.aac)**: File âm thanh hoàn chỉnh (Giọng đọc AI + Nhạc nền đại dương + Tiếng sóng).
