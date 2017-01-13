#!usr/bin/python3
# -*-coding: utf-8 -*-

from PySide import QtGui, QtCore
from configure import (WINDOWS_WIDTH, WINDOWS_HEIGHT, TILE_WIDTH, TILE_HEIGHT, ANIMATION_FRAME, ANIMATION_IMAGE_FRAME,
                       SCENE_WIDTH, SCENE_HEIGHT)

camera_x = 0
camera_y = 0

gradient_001 = QtGui.QRadialGradient(20, 50, 500, 10, 50)
gradient_001.setColorAt(0, QtGui.QColor(100, 100, 100))
gradient_001.setColorAt(0.5, QtGui.QColor(255, 255, 0))
gradient_001.setColorAt(1, QtGui.QColor(100, 100, 100))
brush_001 = QtGui.QBrush(gradient_001)

gradient_002 = QtGui.QRadialGradient(20, 50, 500, 10, 50)
gradient_002.setColorAt(0, QtGui.QColor(100, 100, 100))
gradient_002.setColorAt(0.5, QtGui.QColor(255, 0, 0))
gradient_002.setColorAt(1, QtGui.QColor(100, 100, 100))
brush_002 = QtGui.QBrush(gradient_002)

gradient_003 = QtGui.QRadialGradient(20, 50, 500, 10, 50)
gradient_003.setColorAt(0, QtGui.QColor(100, 100, 100))
gradient_003.setColorAt(0.5, QtGui.QColor(0, 255, 0))
gradient_003.setColorAt(1, QtGui.QColor(100, 100, 100))
brush_003 = QtGui.QBrush(gradient_003)

gradients = [gradient_001, gradient_002, gradient_003]

class Resources(object):
    ground_image = None
    obstacle_image = None
    hero_image = None
    npc_image = None
    character_images = {}
    obstacle_images = None
    ground_images = {}
    gradient_image = None


class CombinePixmap(object):
    def __init__(self, path, image_width, image_height, image_total, line_count=10):
        super().__init__()
        image = QtGui.QPixmap(path)
        self.path = path
        self.line_count = line_count
        self.image_width = image_width
        self.image_height = image_height
        self._images = []
        for i in range(image_total):
            x = i % self.line_count
            y = i // self.line_count
            self._images.append(image.copy(x * self.image_width, y * self.image_height,
                                           self.image_width, self.image_height))

    def get_image(self, identity):
        return self._images[identity]


class DrawObject(QtGui.QGraphicsItem):
    def __init__(self, image, frames, centre_x=0.5, centre_y=0.5):
        super(DrawObject, self).__init__()
        self.current_frame = 0
        self.draw_image = image
        self.centre_x = centre_x
        self.centre_y = centre_y
        self.frames = frames

        self._image = None
        self.pos_x = None
        self.pos_y = None

        self.moving_step = None
        self.total_step = None
        self.previous_x = None
        self.previous_y = None
        self.animation = None

        self.image_width = self.draw_image.image_width
        self.image_height = self.draw_image.image_height

        self._state = None
        self.set_moving(False)
        self.next_opacity = 0.01
        self.setOpacity(0.01)

    def set_moving(self, moving):
        if moving:
            self._state = DrawObjectMoving
        else:
            self._state = DrawObjectNotMoving

    def boundingRect(self):
        return QtCore.QRectF(-self.centre_x * self.image_width,
                             -self.centre_y * self.image_height,
                             self.image_width, self.image_height)

    def update(self):
        self.update_pos()

    def paint(self, painter, option, widget):
        if self.next_opacity > self.opacity() + 0.1:
            self.setOpacity(self.opacity() + 0.1)
        elif self.next_opacity < self.opacity() - 0.1:
            self.setOpacity(self.opacity() - 0.1)
        else:
            self.setOpacity(self.next_opacity)
        self.current_frame += 1
        if self.current_frame // ANIMATION_IMAGE_FRAME == len(self.frames):
            self.current_frame = 0
        if not self.current_frame % ANIMATION_IMAGE_FRAME:
            self._image = self.draw_image.get_image(self.frames[self.current_frame // ANIMATION_IMAGE_FRAME])
        painter.drawPixmap(-self.centre_x * self.image_width,
                           -self.centre_y * self.image_height,
                           self.image_width, self.image_height, self._image)

    def initialize(self, pos_x, pos_y):
        self._state.initialize(self, pos_x, pos_y)

    def update_pos(self):
        self._state.update_pos(self)

    def animation_move(self, nx, ny, total_step=ANIMATION_FRAME):
        self.animation = QtGui.QGraphicsItemAnimation()
        self.animation.setItem(self)
        self.animation.setPosAt(1, QtCore.QPointF(nx, ny))
        self.moving_step = 0
        self.total_step = total_step
        self.pos_x = nx
        self.pos_y = ny
        self.set_moving(True)

    def move_check(self):
        self._state.move_check(self)


class DrawObjectMoving(DrawObject):
    @staticmethod
    def update_pos(conn):
        conn.moving_step += 1
        conn.animation.setStep(conn.moving_step / conn.total_step)
        if conn.moving_step >= conn.total_step:
            conn.set_moving(False)
            conn.animation = None
            conn.moving_step = None
            conn.total_step = None

    @staticmethod
    def initialize(conn, pos_x, pos_y):
        conn.setPos(pos_x * TILE_WIDTH - conn.pos_x + conn.pos().x(),
                    pos_y * TILE_HEIGHT - conn.pos_y + conn.pos().y())
        conn.animation.setPosAt(0, conn.pos())
        conn.pos_x = pos_x * TILE_WIDTH
        conn.pos_y = pos_y * TILE_HEIGHT
        conn.animation.setPosAt(1, QtCore.QPointF(conn.pos_x, conn.pos_y))


class DrawObjectNotMoving(DrawObject):
    @staticmethod
    def update_pos(conn):
        conn.setPos(conn.pos_x, conn.pos_y)

    @staticmethod
    def initialize(conn, pos_x, pos_y):
        conn.pos_x = pos_x * TILE_WIDTH
        conn.pos_y = pos_y * TILE_HEIGHT
        conn.setPos(conn.pos_x, conn.pos_y)
        conn._image = conn.draw_image.get_image(conn.frames[0])


class Shadow(QtGui.QGraphicsEllipseItem):
    def __init__(self, parent):
        super().__init__(parent)

        self.setRect(0, 0, self.parentItem().rigid_size * TILE_WIDTH, self.parentItem().rigid_size * TILE_HEIGHT)
        self.setPos(-self.parentItem().rigid_size * TILE_WIDTH / 2, -self.parentItem().rigid_size * TILE_HEIGHT / 2)
        self.setFlag(self.ItemStacksBehindParent, True)
        self.setZValue(0)
        self.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0, 0)))
        self.setBrush(QtGui.QBrush(QtGui.QColor(0, 0, 0, 100)))


class Gradient(QtGui.QGraphicsPixmapItem):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setPixmap(Resources.gradient_image)

    def setPos(self, *args):
        super().setPos(*args)
        self.moveBy(-TILE_WIDTH, -TILE_HEIGHT)

    def paint(self, painter, option, widget):
        next_opacity = 1.01 - self.parent.next_opacity
        if next_opacity > self.opacity() + 0.1:
            self.setOpacity(self.opacity() + 0.1)
        elif next_opacity < self.opacity() - 0.1:
            self.setOpacity(self.opacity() - 0.1)
        else:
            self.setOpacity(next_opacity)
        super().paint(painter, option, widget)


class GameScene(QtGui.QGraphicsScene):
    """
    """
    def __init__(self, parent=None, f=0):
        super(GameScene, self).__init__(parent, f)


class GameView(QtGui.QGraphicsView):
    def __init__(self, scene, parent=None):
        super(GameView, self).__init__(scene, parent)
        self.setViewportUpdateMode(self.NoViewportUpdate)
        self.center = None
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.set_center(scene.player)
        self.setBackgroundBrush(QtGui.QBrush(QtCore.Qt.black))
        self.setMouseTracking(True)
        self.show()

    def set_center(self, item):
        self.center = item
        self.centerOn(self.center)

    def update(self):
        self.viewport().update()
        self.scene().update()
        if self.center is not None:
            self.setSceneRect(self.center.x() - SCENE_WIDTH, self.center.y() - SCENE_HEIGHT,
                              SCENE_WIDTH << 1, SCENE_HEIGHT << 1)
            self.centerOn(self.center.pos() + QtCore.QPointF(0, TILE_HEIGHT >> 1))

    def drawForeground(self, painter, rect):
        painter.fillRect(rect, QtGui.QColor(100, 100, 0, 100))


class MainWindow(QtGui.QWidget):
    def __init__(self, parent=None, f=0):
        super(MainWindow, self).__init__(parent, f)
        self.setFixedSize(WINDOWS_WIDTH, WINDOWS_HEIGHT)
        self.show()


def test():
    pass

if __name__ == "__main__":
    test()
