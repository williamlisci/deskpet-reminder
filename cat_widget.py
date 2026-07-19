import random
import math
from PyQt6.QtWidgets import QWidget, QLabel, QApplication
from PyQt6.QtGui import QPixmap, QCursor, QTransform
from PyQt6.QtCore import Qt, QTimer, QPoint
from resource_path import resource_path

CAT_SIZE = 35

IMAGE_PATHS = {
    "sit": "assets/cat/sit.png",
    "walk": "assets/cat/walk.png",
    "jump": "assets/cat/jump.png",
}

FLEE_DISTANCE = 100
WALK_SPEED = 2
FLEE_SPEED = 6
TICK_MS = 30
FLEE_BLINK_TICKS = 4

GROUND_BAND_HEIGHT = 4     # dải dọc mèo được đi lại (giữ nhỏ để bám sát 1 hàng ngang)
TASKBAR_GAP = 10           # bù trừ thêm: số âm = đẩy mèo XUỐNG gần taskbar hơn, số dương = đẩy LÊN

STATE_SIT = "sit"
STATE_WALK = "walk"
STATE_JUMP = "jump"
STATE_FLEE = "flee"

STATE_TO_IMAGE = {
    STATE_SIT: "sit",
    STATE_WALK: "walk",
    STATE_JUMP: "jump",
    STATE_FLEE: "walk",
}


class CatWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowTransparentForInput
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(CAT_SIZE, CAT_SIZE)

        self.pixmaps_right = {}
        self.pixmaps_left = {}
        for key, path in IMAGE_PATHS.items():
            pm = QPixmap(resource_path(path))
            self.pixmaps_right[key] = pm
            self.pixmaps_left[key] = pm.transformed(QTransform().scale(-1, 1))

        self.label = QLabel(self)
        self.label.setFixedSize(CAT_SIZE, CAT_SIZE)
        self.label.setScaledContents(True)

        screen = QApplication.primaryScreen()
        if screen is None:
            raise RuntimeError("No screen available")

        # Dùng availableGeometry() để tự động loại trừ vùng taskbar chiếm dụng
        avail_geo = screen.availableGeometry()

        self.screen_width = avail_geo.width()
        # Cạnh dưới của vùng khả dụng (đã trừ taskbar) chính là "mặt đất" của mèo
        self.ground_y = avail_geo.y() + avail_geo.height() - CAT_SIZE + TASKBAR_GAP
        # Giới hạn trên của dải đi lại: từ mặt đất lùi lên GROUND_BAND_HEIGHT px
        self.min_y = max(avail_geo.y(), self.ground_y - GROUND_BAND_HEIGHT)
        self.screen_x_offset = avail_geo.x()

        start_x = self.screen_x_offset + random.randint(0, self.screen_width - CAT_SIZE)
        start_y = random.randint(self.min_y, self.ground_y)
        self.move(start_x, start_y)

        self.state = STATE_SIT
        self.direction = QPoint(0, 0)
        self.facing_right = True
        self.state_timer_counter = 0
        self.next_state_change = random.randint(60, 150)

        self.jump_ticks_left = 0
        self.state_before_jump = STATE_SIT

        self.flee_blink_counter = 0
        self.flee_blink_image = "walk"

        self._apply_sprite()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_cat)
        self.timer.start(TICK_MS)

    def _apply_sprite(self):
        if self.state == STATE_FLEE:
            image_key = self.flee_blink_image
        else:
            image_key = STATE_TO_IMAGE[self.state]
        source = self.pixmaps_right if self.facing_right else self.pixmaps_left
        self.label.setPixmap(source[image_key])

    def update_cat(self):
        mouse_pos = QCursor.pos()
        cat_center = QPoint(self.x() + CAT_SIZE // 2, self.y() + CAT_SIZE // 2)
        dx = cat_center.x() - mouse_pos.x()
        dy = cat_center.y() - mouse_pos.y()
        distance = (dx ** 2 + dy ** 2) ** 0.5

        old_state = self.state
        old_flee_image = self.flee_blink_image

        if distance < FLEE_DISTANCE:
            self.state = STATE_FLEE
            if distance > 0:
                self.direction = QPoint(
                    int(FLEE_SPEED * dx / distance),
                    int(FLEE_SPEED * dy / distance)
                )
            self.state_timer_counter = 0
            self.next_state_change = random.randint(40, 80)
            self.jump_ticks_left = 0

            self.flee_blink_counter += 1
            if self.flee_blink_counter >= FLEE_BLINK_TICKS:
                self.flee_blink_counter = 0
                self.flee_blink_image = "jump" if self.flee_blink_image == "walk" else "walk"
        elif self.state == STATE_JUMP:
            self.jump_ticks_left -= 1
            if self.jump_ticks_left <= 0:
                self.state = self.state_before_jump
                self.state_timer_counter = 0
                self.next_state_change = random.randint(60, 150)
        else:
            self.state_timer_counter += 1
            if self.state_timer_counter >= self.next_state_change:
                self._pick_new_behavior()

        self._move_step()

        if self.state != old_state or (self.state == STATE_FLEE and self.flee_blink_image != old_flee_image):
            self._apply_sprite()

    def _pick_new_behavior(self):
        self.state_timer_counter = 0
        self.next_state_change = random.randint(60, 180)

        choice = random.choices(
            [STATE_SIT, STATE_WALK, STATE_JUMP],
            weights=[20, 55, 25],
            k=1
        )[0]

        if choice == STATE_JUMP:
            self.jump_ticks_left = random.randint(10, 20)
            self.state_before_jump = STATE_WALK
            self.state = STATE_JUMP
            facing = 1 if self.facing_right else -1
            self.direction = QPoint(facing * WALK_SPEED, 0)
            return

        self.state = choice
        if choice == STATE_WALK:
            # Chỉ đi ngang trái/phải, không đi dọc lên xuống nhiều (mèo ở trên "mặt đất")
            angle = random.choice([0.0, math.pi])  # trái hoặc phải
            angle += random.uniform(-0.3, 0.3)      # thêm chút lệch nhẹ tự nhiên
            self.direction = QPoint(
                int(WALK_SPEED * math.cos(angle)),
                int(WALK_SPEED * math.sin(angle) * 0.3)  # giảm hẳn thành phần dọc
            )
        else:
            self.direction = QPoint(0, 0)

    def _move_step(self):
        if self.state == STATE_SIT:
            return

        new_x = self.x() + self.direction.x()
        new_y = self.y() + self.direction.y()

        min_x = self.screen_x_offset
        max_x = self.screen_x_offset + self.screen_width - CAT_SIZE

        bounced = False
        if new_x < min_x or new_x > max_x:
            self.direction = QPoint(-self.direction.x(), self.direction.y())
            bounced = True
        if new_y < self.min_y or new_y > self.ground_y:
            self.direction = QPoint(self.direction.x(), -self.direction.y())
            bounced = True

        if bounced:
            new_x = max(min_x, min(new_x, max_x))
            new_y = max(self.min_y, min(new_y, self.ground_y))

        if self.direction.x() != 0:
            should_face_right = self.direction.x() > 0
            if should_face_right != self.facing_right:
                self.facing_right = should_face_right
                self._apply_sprite()

        self.move(new_x, new_y)
