import sys
import os
import winreg

APP_NAME = "DeskPetReminder"
RUN_KEY_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"


def _get_exe_path() -> str:
    """
    Trả về đường dẫn thực thi để đăng ký autostart.
    - Nếu đang chạy dưới dạng .exe đã đóng gói (PyInstaller) -> dùng sys.executable
    - Nếu đang chạy bằng python main.py (dev mode) -> dùng pythonw.exe + đường dẫn script
    """
    if getattr(sys, "frozen", False):
        # Đang chạy từ file .exe đóng gói
        return f'"{sys.executable}"'
    else:
        # Đang chạy dev bằng python, dùng pythonw để không hiện cửa sổ console đen
        python_dir = os.path.dirname(sys.executable)
        pythonw = os.path.join(python_dir, "pythonw.exe")
        script_path = os.path.abspath(sys.argv[0])
        return f'"{pythonw}" "{script_path}"'


def is_autostart_enabled() -> bool:
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY_PATH, 0, winreg.KEY_READ)
        try:
            winreg.QueryValueEx(key, APP_NAME)
            return True
        except FileNotFoundError:
            return False
        finally:
            winreg.CloseKey(key)
    except OSError:
        return False


def enable_autostart():
    exe_path = _get_exe_path()
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY_PATH, 0, winreg.KEY_SET_VALUE)
    winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, exe_path)
    winreg.CloseKey(key)


def disable_autostart():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY_PATH, 0, winreg.KEY_SET_VALUE)
        try:
            winreg.DeleteValue(key, APP_NAME)
        except FileNotFoundError:
            pass
        finally:
            winreg.CloseKey(key)
    except OSError:
        pass
