#!usr/bin/python3
# -*-coding: utf-8 -*-

from random import randrange
from function import double_range, save_byte, load_byte, Pos
from graphics import Resources as Res
import graphics
import character
import interface
from configure import LOCAL_SIZE, GLOBAL_HEIGHT, GLOBAL_WIDTH, TILE_WIDTH, TILE_HEIGHT, GAME_UPDATE_TIME
from PyQt5.QtCore import Qt, QTimer

map_identity = 0


class Tile(graphics.DrawObject):
    def __init__(self, x, y, tile_type, local_map, image, frames=None):
        self.x = x
        self.y = y
        self.local_map = local_map
        self.tile_type = tile_type
        self.visible = False
        if frames is None:
            frames = [self.tile_type]
        super().__init__(image, frames)
        self.rigid_body = None
        self.scene_pos_x, self.scene_pos_y = None, None
        self.setZValue(-3)
        self.image_width = TILE_WIDTH
        self.image_height = TILE_HEIGHT
        self.gradient = graphics.Gradient(self)

    def __del__(self):
        del self.gradient
        self.gradient = None

    def setPos(self, *args):
        super().setPos(*args)
        self.gradient.setPos(*args)

    def itemChange(self, change, value):
        super().itemChange(change, value)
        if change == self.ItemSceneChange:
            if value is None:
                self.scene().removeItem(self.gradient)
            else:
                value.addItem(self.gradient)
        return value


class Maps(object):
    """
    Maps Object -- Basic type of maps; Its width & height is constant, unless creating a new one;
    property:
        get_width, get_height
    function:
        random_create: create a randomized content with given arguments as a tuple
    """
    def __init__(self):
        self._width = None
        self._height = None
        self.contents = None

    def _new(self, width, height, content=None):
        self._width = width
        self._height = height
        self.contents = [[content for y in range(height)] for x in range(width)]

    def __getitem__(self, index):
        assert isinstance(self.contents, list), "content not set or incorrect!"
        assert isinstance(self.contents[index], list), "content not set or incorrect!"
        return self.contents[index]

    def random_create(self, *content_types):
        assert isinstance(self.contents, list), "content not set or incorrect!"
        for (x, y) in double_range(self.get_width, self.get_height):
                self.contents[x][y] = content_types[randrange(len(content_types))]

    @property
    def get_width(self):
        return self._width

    @property
    def get_height(self):
        return self._height


class SavingMaps(Maps):

    """
    SavingMaps Object -- maps can be saved in a file
    function:
        new_init: create a new map
        load_init:load map from file
        saving:save map from file
    property:
        file_path: the path where file locating
    """
    def __init__(self):
        super(SavingMaps, self).__init__()
        self.file_path = None
    
    def new_init(self, width, height, content=None):
        self._new(width, height, content)

    def load_init(self):
        assert self.file_path, "file path not set!"
        result = load_byte(self.file_path)
        if result:
            self._width, self._height, self.contents = result
            return True
        else:
            return False

    def saving(self):
        assert self.contents, "Contents not initialize!"
        save_byte((self.get_width, self.get_height, self.contents), self.file_path)


class LocalMap(Maps):
    """
    LocalMap object -- maps where rigid bodies and items locating; If its content is none, the tile there remain blank;
    function:
        new_init: creating a new map;
        load_init: creating map from file;
        save: saving map to file;
    """
    def __init__(self, x=0, y=0):
        super(LocalMap, self).__init__()
        global map_identity
        self.identity = map_identity
        self.file_path = "sav//m%08d.dat" % self.identity
        self.x, self.y = x, y
        map_identity += 1

    def load_init(self, scene):
        result = load_byte(self.file_path)
        if result:
            self._width, self._height, layout, obstacle_layout, character_layout = result
            self.contents = [[None for x in range(self._height)] for y in range(self._width)]
            index = 0
            for x, y in double_range(self._width, self._height):
                self.contents[x][y] = Tile(x, y, layout[index], self, Res.ground_image)
                scene.addItem(self.contents[x][y])
                if obstacle_layout[index] is not None:
                    rigid_body_save = obstacle_layout[index]
                    self.contents[x][y].rigid_body = character.Obstacle.load(
                        rigid_body_save, self, self.contents[x][y], Res.obstacle_images)
                    scene.addItem(self.contents[x][y].rigid_body)
                if character_layout[index] is not None:
                    self.contents[x][y].rigid_body = character.NonePlayer.load(
                        character_layout[index], self.contents[x][y], scene, scene.current_time)
                    scene.characters.append(self.contents[x][y].rigid_body)
                    scene.addItem(self.contents[x][y].rigid_body)
                index += 1
            return True
        else:
            return False

    def random_create(self, scene, ground_types, obstacle_types):
        for (x, y) in double_range(self.get_width, self.get_height):
            self.contents[x][y] = Tile(x, y, ground_types[randrange(len(ground_types))], self, Res.ground_image)
            scene.addItem(self.contents[x][y])
            check1 = randrange(20)
            check1_1 = randrange(5)
            check2 = randrange(20)
            if not check1:
                if check1_1:
                    self.contents[x][y].rigid_body = character.Obstacle.create(
                        obstacle_types[randrange(len(obstacle_types))], "forest_small", scene, self.contents[x][y],
                        Res.obstacle_images, centre_y=0.9)
                else:
                    self.contents[x][y].rigid_body = character.Obstacle.create(
                        randrange(4), "forest_large", scene, self.contents[x][y],
                        Res.obstacle_images, rigid_height=4.0, rigid_size=2.0, centre_y=0.9)
                scene.addItem(self.contents[x][y].rigid_body)
            elif not check2:
                self.contents[x][y].rigid_body = character.NonePlayer(
                    (("female", "male", "others")[randrange(3)], randrange(3)), scene, self.contents[x][y], [0],
                    action_time=scene.current_time)
                scene.characters.append(self.contents[x][y].rigid_body)
                scene.addItem(self.contents[x][y].rigid_body)

    def install(self, scene, width=LOCAL_SIZE, height=LOCAL_SIZE):
        assert isinstance(scene, Scene)
        if not self.load_init(scene):
            self._new(width, height, 0)
            self.random_create(scene, [4, 5, 6], [0, 1, 4, 5])

    def save(self):
        layout = [self.contents[x][y].tile_type for x, y in double_range(self.get_width, self.get_height)]
        obstacle_layout = []
        character_layout = []
        for x, y in double_range(self.get_width, self.get_height):
            if isinstance(self.contents[x][y].rigid_body, character.Obstacle):
                obstacle_layout.append(self.contents[x][y].rigid_body.save_type())
            else:
                obstacle_layout.append(None)
            if isinstance(self.contents[x][y].rigid_body, character.Character):
                character_layout.append(self.contents[x][y].rigid_body.save_type())
            else:
                character_layout.append(None)
        save_byte((self.get_width, self.get_height, layout, obstacle_layout, character_layout), self.file_path)

    def uninstall(self, scene):
        self.save()
        for x, y in double_range(self.get_width, self.get_height):
            temp, self.contents[x][y] = self.contents[x][y], None
            scene.removeItem(temp)
            if isinstance(temp.rigid_body, character.Obstacle):
                scene.removeItem(temp.rigid_body)
                del temp.rigid_body
            elif isinstance(temp.rigid_body, character.Character):
                scene.removeItem(temp.rigid_body)
                if temp.rigid_body in scene.characters:
                    scene.characters.remove(temp.rigid_body)
                del temp.rigid_body
            del temp
        self.contents = None

    def get_tile(self, x, y):
        return self.contents[x][y]


class GlobalMap(SavingMaps):
    """
    GlobalMap object -- map contain the whole world; Including normal local map;
    """
    def __init__(self):
        super(GlobalMap, self).__init__()
        self.file_path = "sav//map.dat"
        if not self.load_init():
            self.new_init(GLOBAL_WIDTH, GLOBAL_HEIGHT)
            self.contents = [[LocalMap(j, i) for i in range(GLOBAL_HEIGHT)] for j in range(GLOBAL_WIDTH)]
        self.saving()


class Scene(graphics.GameScene):
    """
    Scene object -- contain a GlobalMap and temporary 3 * 3 LocalMaps
    """
    def __init__(self, parent=None):
        super(Scene, self).__init__(parent)
        self.global_map = GlobalMap()
        self._state = None

        self.player_action = None
        self.player_args = None
        self.control_function = None
        self.control_target = None

        self.current_time = 0
        self.pos = None
        self.player = None
        self.characters = []
        self.centre_pos = None
        self.contents = []
        self.ground_cursor = None

        self.text_out = None
        self.window = None

        self.time_count0 = 0
        self.mousePos = None
        self.control_table = None

        self.game_update_end_flag = True
        self.update_end_flag = True
        self.game_timer = QTimer()
        self.game_timer.timeout.connect(self.update_game)
        self.game_timer.start(GAME_UPDATE_TIME)

        self.player_action_function = self.control_none

        if not self.load():
            self.single_flag = False
            self.set_state(SceneMainMap)
            self.set_pos(10, 10)
            self.set_centre_pos(1, 1)
            self.create_player()

        self.player.refresh()

    def set_text_out(self, func):
        self.text_out = func

    def create_player(self):
        self.player = character.Player(
            ("male", 0), self, self.get_tile(0, 0))
        self.get_tile(0, 0).rigid_body = self.player
        self.player.initialize(self.player.tile.scene_pos_x, self.player.tile.scene_pos_y)
        self.addItem(self.player)

    def load_player(self):
        file = load_byte("sav//player.dat")
        if not file:
            return False
        save_data, save_pos_x, save_pos_y = file
        self.set_centre_pos(save_pos_x, save_pos_y)
        self.player = character.Player.load(save_data, self.get_tile(), self)
        self.get_tile().rigid_body = self.player
        self.player.initialize(self.player.tile.scene_pos_x, self.player.tile.scene_pos_y)
        self.addItem(self.player)
        return True

    def save_player(self):
        save_byte((self.player.save_type(), self.player.tile.x, self.player.tile.y),
                  "sav//player.dat")

    def update(self):
        self.update_end_flag = False
        self.player.update_pos()
        for chara in self.characters:
            chara.update_pos()
        if self.mousePos is not None:
            items = self.items(self.mousePos)
            total = 0
            for item in items[::-1]:
                if isinstance(item, character.RigidBody):
                    total += 1
                    if total > 1 and item.rigid_height > 2.0:
                        item.mouse_on = True
        self.update_end_flag = True

    def initialize(self):
        self._state.initialize(self)
        if self.ground_cursor:
            self.ground_cursor.reset()

    def update_game(self):
        self.game_update_end_flag = False
        if self.current_time < self.player.action_time:
            self.current_time += 1
            for chara in self.characters:
                chara.update_game()
            self.player.update_game()
        elif self.control_function is not None:
            self.control_convert()
        elif self.player_action is not None:
            self.control_game()
            self.check_map()
            self.player.refresh()
        elif self.ground_cursor is not None:
            self.removeItem(self.ground_cursor)
            del self.ground_cursor
            self.ground_cursor = None
        for chara in self.characters:
            chara.auto_update(self.current_time)
        self.game_update_end_flag = True

    def control_convert(self):
        if self.control_function == "auto_moving":
            if self.ground_cursor is not None:
                self.removeItem(self.ground_cursor)
                del self.ground_cursor
                self.ground_cursor = None
            self.ground_cursor = interface.GroundCursor(self.control_target)
            self.addItem(self.ground_cursor)

            dx = self.control_target.scene_pos_x - self.player.tile.scene_pos_x
            dy = self.control_target.scene_pos_y - self.player.tile.scene_pos_y
            self.player_action = "auto_moving"
            self.player_action_function = self.control_auto_moving
            self.player_args = [dx, dy]
            self.control_function = None
            self.control_target = None

    def control_game(self):
        self.player_action_function(self)

    @staticmethod
    def control_none(self):
        return

    @staticmethod
    def control_auto_moving(self):
        # # Player moves to a fixed position, pointed by cursor. The arguments contain the dx, dy
        direction = self.player.find_way(self.player_args[0], self.player_args[1])
        self.player_args[0] -= Pos.direction[direction][0]
        self.player_args[1] -= Pos.direction[direction][1]
        if not(self.player_args[0] or self.player_args[1]):
            self.player_args = None
            self.player_action = None
            self.player_action_function = self.control_none
        self.player.control("action_move", [direction])

    # # Check map position depending on the player. If the player moves to another local map, this function does
    # # initialize
    def check_map(self):
        self._state.check_map(self)
        self.save()

    def set_state(self, new_state):
        self._state = new_state

    def draw_scene(self):
        self._state.draw_scene(self)

    def save(self):
        self.player.tile.rigid_body = None
        self.save_player()
        self._state.save(self)
        save_byte((self.pos, self.single_flag, map_identity, character.character_identity),
                  "sav//scene.dat")
        self.player.tile.rigid_body = self.player

    def load(self):
        global map_identity
        result = load_byte("sav//scene.dat")
        if result:
            self.pos, self.single_flag, map_identity, character.character_identity = result
            if self.single_flag:
                self.set_state(SceneSingleMap)
            else:
                self.set_state(SceneMainMap)
            self.set_pos(self.pos.x, self.pos.y)
            if not self.load_player():
                self.create_player()
            return True
        else:
            return False

    def uninstall(self):
        self._state.uninstall(self)

    def set_pos(self, pos_x, pos_y):
        self._state.set_pos(self, pos_x, pos_y)
        self.initialize()

    def set_map(self, local_map):
        if self.contents:
            self.uninstall()
        self.pos = None
        self.contents = local_map
        self.contents.install(self)
        self.single_flag = True
        self.set_state(SceneSingleMap)
        self.initialize()

    def get_width(self):
        return self._state.get_width(self)

    def get_height(self):
        return self._state.get_height(self)

    def get_all_tiles(self):
        for item in self.items():
            if isinstance(item, Tile):
                yield item

    # #get tile response to centre pos
    def get_tile(self, x=0, y=0):
        return self._state.get_tile(self, x, y)

    def get_tile_absolute(self, x, y):
        return self._state.get_tile_absolute(self, x, y)

    def get_centre_absolute(self):
        return self._state.get_centre_absolute(self)

    def set_centre_pos(self, x, y):
        self.centre_pos = Pos(x, y)

    def mousePressEvent(self, event):
        item = self.get_tile_absolute(
            int(event.scenePos().x() / TILE_WIDTH + 0.5), int(event.scenePos().y() / TILE_HEIGHT + 0.5))
        if self.control_table is not None:
            self.control_table.get_sign()
            self.control_table = None
        elif isinstance(item, Tile):
            if event.button() == Qt.RightButton:
                self.control_table = interface.ControlTable(
                    [("MOVE", "auto_moving"), ("OBSERVE", "attack"),
                     ("SKILL", "attack"), ("SOURCE", "attack")], event.screenPos(), item, self)

    def keyPressEvent(self, event):
        direction = character.key_map[event.key()]
        self.player_action, self.player_args = "action_dash", [direction]

    def mouseMoveEvent(self, event):
        self.mousePos = event.scenePos()


class SceneSingleMap(Scene):
    @staticmethod
    def initialize(conn):
        for (x, y) in double_range(conn.contents.width, conn.contents.height):
            tile = conn.contents[x][y]
            tile.scene_pos_x, tile.scene_pos_y = x, y
            tile.initialize(x, y, Res.ground_image)
            if isinstance(tile.rigid_body, character.RigidBody):
                tile.rigid_body.initialize(x, y)

    @staticmethod
    def uninstall(conn):
        conn.contents.uninstall(conn)

    @staticmethod
    def set_pos(conn, pos_x, pos_y):
        assert isinstance(conn.contents, LocalMap)
        conn.contents.uninstall(conn)
        conn.contents = [conn.global_map[x][y] for (x, y) in conn.pos.area()]
        conn.single_flag = False
        conn.set_state(SceneMainMap)

    @staticmethod
    def get_tile(conn, x=0, y=0):
        tx = x + conn.centre_pos.x
        ty = y + conn.centre_pos.y
        if 0 <= tx < conn.contents.width and 0 <= ty < conn.contents.height:
            return conn.contents[tx][ty]
        return None

    @staticmethod
    def get_tile_absolute(conn, x, y):
        return conn.contents[x][y]

    @staticmethod
    def get_centre_absolute(conn):
        return conn.centre_pos


class SceneMainMap(Scene):
    @staticmethod
    def save(conn):
        for i in conn.contents:
            i.save()

    @staticmethod
    def initialize(conn):
        for i in range(9):
            for x, y in double_range(LOCAL_SIZE, LOCAL_SIZE):
                conn.contents[i][x][y].scene_pos_x = (1 + Pos.direction[i][0]) * LOCAL_SIZE + x
                conn.contents[i][x][y].scene_pos_y = (1 + Pos.direction[i][1]) * LOCAL_SIZE + y
                conn.contents[i][x][y].initialize(conn.contents[i][x][y].scene_pos_x,
                                                  conn.contents[i][x][y].scene_pos_y)
                if conn.contents[i][x][y].rigid_body is not None:
                    conn.contents[i][x][y].rigid_body.initialize(conn.contents[i][x][y].scene_pos_x,
                                                                 conn.contents[i][x][y].scene_pos_y)

    @staticmethod
    def get_width(conn):
        return 3 * LOCAL_SIZE

    @staticmethod
    def get_height(conn):
        return 3 * LOCAL_SIZE

    @staticmethod
    def uninstall(conn):
        for i in conn.contents:
            i.uninstall(conn)
        conn.contents = []

    @staticmethod
    def check_map(conn):
        if conn.player.tile.local_map != conn.contents[0]:
            conn.set_pos(conn.player.tile.local_map.x, conn.player.tile.local_map.y)

    @staticmethod
    def set_pos(conn, pos_x, pos_y):
        conn.pos = Pos(pos_x, pos_y, conn.global_map.get_width, conn.global_map.get_height)
        assert isinstance(conn.contents, list)
        old_maps = conn.contents.copy()
        new_maps = [conn.global_map[x][y] for (x, y) in conn.pos.area()]
        for local_map in new_maps:
            if local_map not in old_maps:
                local_map.install(conn, LOCAL_SIZE, LOCAL_SIZE)
        for local_map in old_maps:
            if local_map not in new_maps:
                local_map.uninstall(conn)
        conn.contents = new_maps

    @staticmethod
    def get_tile(conn, x=0, y=0):
        tx = x + conn.centre_pos.x
        ty = y + conn.centre_pos.y
        mx, my = 0, 0
        if tx >= LOCAL_SIZE:
            tx -= LOCAL_SIZE
            mx = 1
        elif tx < 0:
            tx += LOCAL_SIZE
            mx = -1
        if ty >= LOCAL_SIZE:
            ty -= LOCAL_SIZE
            my = 1
        elif ty < 0:
            ty += LOCAL_SIZE
            my = -1
        if 0 <= tx < LOCAL_SIZE and 0 <= ty < LOCAL_SIZE:
            return conn.contents[Pos.r_direction[(mx, my)]][tx][ty]
        return None

    @staticmethod
    def get_tile_absolute(conn, x, y):
        tx = x % LOCAL_SIZE
        ty = y % LOCAL_SIZE
        mx = x // LOCAL_SIZE - 1
        my = y // LOCAL_SIZE - 1
        if (mx, my) in Pos.r_direction.keys():
            return conn.contents[Pos.r_direction[(mx, my)]][tx][ty]
        return None

    @staticmethod
    def get_centre_absolute(conn):
        return Pos(conn.centre_pos.x + LOCAL_SIZE, conn.centre_pos.y + LOCAL_SIZE)
