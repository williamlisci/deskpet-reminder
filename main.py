import sys
from PyQt6.QtWidgets import (
    QApplication, QSystemTrayIcon, QMenu, QMessageBox
)
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QTimer
from quote_service import get_daily_quote
from cat_widget import CatWidget
from autostart import is_autostart_enabled, enable_autostart, disable_autostart
from resource_path import resource_path

APP_NAME = "DeskPet Reminder"

class ReminderApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)

        # 1. Khởi tạo QSystemTrayIcon mà không cần tham số để tránh lỗi Linter
        self.tray = QSystemTrayIcon()

        # 2. Set icon sau bằng phương thức riêng (an toàn hơn)
        self.tray.setIcon(QIcon(resource_path("icon.ico")))
        self.tray.setToolTip(APP_NAME)

        # Con mèo desktop pet
        self.cat = CatWidget()
        self.cat.show()

        # 3. Tạo Menu
        menu = QMenu()

        # Tạo QAction tường minh
        self.action_30 = QAction("Nhắc nghỉ mỗi 30 phút")
        self.action_30.setCheckable(True)
        self.action_30.triggered.connect(lambda: self.set_interval(30))
        menu.addAction(self.action_30)

        self.action_60 = QAction("Nhắc nghỉ mỗi 60 phút")
        self.action_60.setCheckable(True)
        self.action_60.triggered.connect(lambda: self.set_interval(60))
        menu.addAction(self.action_60)

        menu.addSeparator()

        # Action thoát
        self.action_quit = QAction("Thoát")
        self.action_quit.triggered.connect(self.app.quit)

        self.action_autostart = QAction("Khởi động cùng Windows")
        self.action_autostart.setCheckable(True)
        self.action_autostart.setChecked(is_autostart_enabled())
        self.action_autostart.triggered.connect(self.toggle_autostart)

        menu.addAction(self.action_autostart)
        menu.addSeparator()
        menu.addAction(self.action_quit)

        self.tray.setContextMenu(menu)
        self.tray.show()

        # Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.show_reminder)
        self.set_interval(30)
        # dòng test tạm thời
        # self.show_reminder()

    def set_interval(self, minutes: int):
        self.action_30.setChecked(minutes == 30)
        self.action_60.setChecked(minutes == 60)
        self.timer.stop()
        self.timer.start(minutes * 60 * 1000)

        # Để tránh lỗi nếu icon chưa load được, showMessage vẫn hoạt động tốt
        self.tray.showMessage(
            APP_NAME,
            f"Đã đặt nhắc nghỉ mỗi {minutes} phút.",
            QSystemTrayIcon.MessageIcon.Information,
            3000
        )

    def show_reminder(self):
        quote = get_daily_quote()
        message = f"Đã đến giờ nghỉ ngơi! Đứng dậy vươn vai nhé 🧘\n\n💬 {quote}"
        QMessageBox.information(None, APP_NAME, message)

    def toggle_autostart(self):
            if self.action_autostart.isChecked():
                enable_autostart()
                self.tray.showMessage(
                    APP_NAME, "Đã bật khởi động cùng Windows.",
                    QSystemTrayIcon.MessageIcon.Information, 2000
                )
            else:
                disable_autostart()
                self.tray.showMessage(
                    APP_NAME, "Đã tắt khởi động cùng Windows.",
                    QSystemTrayIcon.MessageIcon.Information, 2000
                )

    def run(self):
        sys.exit(self.app.exec())

if __name__ == "__main__":
    reminder = ReminderApp()
    reminder.run()
