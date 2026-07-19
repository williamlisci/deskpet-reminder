# DeskPet Reminder 🐈

Ứng dụng nhắc nghỉ ngơi định kỳ (30/60 phút) kèm câu quote động lực, cùng một chú mèo đen desktop pet chạy trên màn hình.

## Tính năng
- Nhắc nghỉ ngơi mỗi 30 hoặc 60 phút (tuỳ chọn qua system tray)
- Hiển thị câu quote động lực lấy từ ZenQuotes API, đổi mỗi ngày, có fallback offline
- Mèo desktop pet: tự đi lại ngẫu nhiên (ngồi/đi bộ/nhảy), chạy trốn khi chuột lại gần
- Tự khởi động cùng Windows (tuỳ chọn)
- Chạy nền qua system tray, không chiếm taskbar

## Cài đặt (người dùng cuối)
Tải file cài đặt mới nhất tại mục [Releases](../../releases), chạy `DeskPetReminder_Setup.exe` và làm theo hướng dẫn.

## Chạy từ source (dành cho dev)
```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## Build .exe
```powershell
pyinstaller --name "DeskPetReminder" --onefile --noconsole --icon=icon.ico --add-data "icon.ico;." --add-data "assets;assets" main.py
```

## Build installer (Inno Setup 7)
Mở `installer.iss` bằng Inno Setup 7 Compiler, nhấn F9 để build.

## Yêu cầu hệ thống
- Windows 11 64-bit
- Python 3.14.6 (nếu chạy từ source)

## khác
- xóa nền trắng cho ảnh mèo : python remove_bg.py
- pip freeze > requirements.txt
- pip install -r requirements.txt

## Giấy phép
(bạn tự chọn: MIT / Apache 2.0 / v.v. — hoặc để trống nếu chưa quyết định)
