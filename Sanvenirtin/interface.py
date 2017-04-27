#!usr/bin/python3
# -*-coding: utf-8 -*-

import math
import time
import graphics
from PyQt5.QtWidgets import QGraphicsPixmapItem, QWidget, QHBoxLayout, QTextEdit
from PyQt5.QtGui import QPixmap, QColor, QPainter, QBrush, QRadialGradient, QPainterPath, QPen
from PyQt5.QtCore import Qt, QRect, QTimer, QPoint, QRectF
from configure import (SCENE_WIDTH, SCENE_HEIGHT, INTERFACE_WIDTH, INTERFACE_HEIGHT, TEXT_HEIGHT, FPS,
                       TILE_WIDTH, TILE_HEIGHT)

text_out = None


class GroundCursor(QGraphicsPixmapItem):
    def __init__(self, tile):
        super().__init__(QPixmap("res//gui//ground_cursor.png"))
        self.setZValue(0)
        self.tile = tile
        self.reset()

    def setPos(self, *args):
        super().setPos(*args)
        self.moveBy(-self.pixmap().width() >> 1, -self.pixmap().height() >> 1)

    def paint(self, *args):
        self.setOpacity((math.sin(time.time() * 5) + 1.0) / 5 + 0.5)
        super().paint(*args)

    def reset(self):
        self.setPos(self.tile.scenePos())


class PropertyIcon(QWidget):
    def __init__(self, icon, color, text, value, parent=None):
        super().__init__(parent)
        self.property_text = text
        self.property_icon = QPixmap(icon)
        assert isinstance(color, QColor)
        self.color = color
        self.value = value
        self.show()

    def paintEvent(self, event):
        if self.value() < 1.0:
            self.color.setAlphaF(min(1, 1 - self.value()))
            color = self.color
        else:
            color_value = max(0, int(510 - 255 * self.value()))
            color = QColor(color_value, color_value, color_value, 255 - color_value)
        painter = QPainter(self)
        rect = QRect(0, TEXT_HEIGHT, self.width(), self.height() - TEXT_HEIGHT)
        painter.fillRect(rect, QBrush(color))
        painter.drawPixmap(rect, self.property_icon)
        painter.drawText(0, 0, self.width(), TEXT_HEIGHT, Qt.AlignHCenter, self.property_text)


class PropertyArea(QWidget):
    def __init__(self, player_status, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        self.health = PropertyIcon("res//gui//badge_vital.png", QColor(0, 255, 0), "HEALTH",
                                   lambda: player_status.health / player_status.use("max_health"), self)
        self.injure = PropertyIcon("res//gui//badge_chilly.png", QColor(255, 0, 0), "INJURE",
                                   lambda: player_status.injure / player_status.use("max_injure"), self)
        self.endure = PropertyIcon("res//gui//badge_holy.png", QColor(255, 255, 0), "ENDURE",
                                   lambda: player_status.endure / player_status.use("max_endure"), self)
        self.energy = PropertyIcon("res//gui//badge_dark.png", QColor(255, 0, 255), "ENERGY",
                                   lambda: player_status.energy / player_status.use("max_energy"), self)
        self.sanity = PropertyIcon("res//gui//badge_flaming.png", QColor(0, 255, 255), "SANITY",
                                   lambda: player_status.sanity / player_status.use("max_sanity"), self)
        layout.addWidget(self.health)
        layout.addWidget(self.injure)
        layout.addWidget(self.endure)
        layout.addWidget(self.energy)
        layout.addWidget(self.sanity)
        self.setLayout(layout)


class RecordArea(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.show()

    def text_out(self, text):
        self.append(text)


class ControlTable(QWidget):
    """
    buttons is a list of tuples. The content of tuple is (button name, button function)
    Clicking a button causing the ControlTable return the function of the button.
    """
    def __init__(self, buttons, pos, target, scene):
        super().__init__(scene.window)
        assert isinstance(buttons, list)
        self.scene = scene
        self.total = len(buttons)
        self.setMouseTracking(True)
        self.resize(TILE_WIDTH << 2, TILE_HEIGHT << 2)

        self.setContentsMargins(10, 10, 10, 10)
        self.buttons = [ControlButton(index, buttons[index][0], buttons[index][1], self) for index in range(self.total)]
        self.target = target

        self.vanishing = False
        self.start = False
        self.opacity = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(1000//FPS)
        self.move(pos - self.parent().pos() - QPoint(TILE_WIDTH * 2.5, TILE_HEIGHT * 3))
        self.show()

    def get_sign(self, func=None):
        for button in self.buttons:
            button.setEnabled(False)
        self.vanishing = True
        self.setEnabled(False)
        self.scene.control_table = None
        if func is None:
            return
        self.scene.control_function = func
        self.scene.control_target = self.target

    def update(self):
        for button in self.buttons:
            button.repaint()
        if self.vanishing:
            self.opacity -= 10
            if self.opacity <= 0:
                self.hide()
                del self
        elif self.start:
            self.opacity += 10
            if self.opacity > 150 + int(50 * math.sin(time.time() * 2)):
                self.start = False
        else:
            self.opacity = 150 + int(50 * math.sin(time.time() * 2))

    def mouseMoveEvent(self, event):
        for button in self.buttons:
            if button.path.contains(event.pos()):
                button.opacity = 255
            else:
                button.opacity = None

    def mousePressEvent(self, event):
        if self.vanishing:
            return
        for button in self.buttons:
            if button.path.contains(event.pos()):
                self.get_sign(button.function)
                return
        self.get_sign()


class ControlButton(QWidget):
    def __init__(self, index, name, func, parent):
        super().__init__(parent)
        self.index = index
        self.name = name
        self.function = func
        self.resize(TILE_WIDTH << 2, TILE_HEIGHT << 2)
        self.show()
        self.opacity = None
        self.setMouseTracking(True)
        self.color = QColor(50 * self.index, 255, 255 - 10 * self.index)
        self.gradient = QRadialGradient(
            50 + 10 * self.index, 50 - 10 * self.index, 500 - 50 * self.index,
            50 + 10 * self.index, 100 - 10 * self.index)
        self.gradient.setColorAt(0, QColor(200, 200, 200))
        self.gradient.setColorAt(0.5, QColor(50 * self.index, 255, 255 - 10 * self.index))
        self.gradient.setColorAt(1, QColor(200, 200, 200))
        self.brush = QBrush(self.gradient)
        self.path = QPainterPath()
        rect = QRectF(TILE_WIDTH * 1.5, TILE_HEIGHT * 1.5, TILE_WIDTH * 1.5, TILE_HEIGHT * 1.5)
        total = self.parent().total - 1
        if total < 3:
            total = 3
        if self.index == 0:
            self.path.arcMoveTo(rect, 90)
            self.path.arcTo(rect, 90, 360)
        else:
            self.path.arcMoveTo(QRectF(self.rect()), 90 + self.index * 360 // total)
            self.path.arcTo(QRectF(self.rect()), 90 + self.index * 360 // total,  360 // total)
            self.path.arcTo(rect, 90 + self.index * 360 // total + 360 // total, -360 // total)
            self.path.arcTo(QRectF(self.rect()), 90 + self.index * 360 // total,  0)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setBrush(self.brush)
        if self.opacity is None or self.parent().vanishing:
            painter.setOpacity(self.parent().opacity / 255)
        else:
            painter.setOpacity(self.opacity / 255)
        pen = QPen(QColor(100, 100, 100, 150))
        pen.setWidth(10)
        painter.setPen(pen)
        painter.drawPath(self.path)
        painter.setPen(QColor(0, 0, 0))
        painter.drawText(self.path.controlPointRect(), Qt.AlignCenter, self.name)


class GameSceneInterface(QWidget):
    def __init__(self, scene, parent=None):
        super().__init__(parent)
        self.scene = scene
        self.scene.window = self
        self.resize(INTERFACE_WIDTH, INTERFACE_HEIGHT)
        self.view = graphics.GameView(self.scene, self)
        self.record_view = RecordArea(self)
        scene.set_text_out(self.record_view.text_out)
        self.property_view = PropertyArea(self.scene.player.status, self)
        self.paint_timer = QTimer()
        self.paint_timer.timeout.connect(self.update)
        self.paint_timer.start(1000 // FPS)

    def resizeEvent(self, event):
        self.view.resize(SCENE_WIDTH, SCENE_HEIGHT)
        self.view.move((self.size().width() - SCENE_WIDTH) // 2, self.size().height() - SCENE_HEIGHT)
        self.property_view.resize((self.size().width() - SCENE_WIDTH) // 2,
                                  (self.size().width() - SCENE_WIDTH) // 10 + TEXT_HEIGHT)
        self.property_view.move(0, self.size().height() - SCENE_HEIGHT)
        self.record_view.resize((self.size().width() - SCENE_WIDTH) // 2, self.size().height() / 2)
        self.record_view.move(0, self.size().height() / 2)

    def update(self):
        if self.scene.game_update_end_flag and self.scene.update_end_flag:
            self.view.update()
            self.property_view.update()
