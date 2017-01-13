#!usr/bin/python3
# -*-coding: utf-8 -*-

"""
Character class

"""
import random
from function import Define as Df, log10 as lg, Pos, double_range, Calculate, sgn
import graphics
from configure import SIGHT_AREA, TILE_HEIGHT, TILE_WIDTH

key_map = {graphics.QtCore.Qt.Key_5: 0,
           graphics.QtCore.Qt.Key_1: 1,
           graphics.QtCore.Qt.Key_2: 2,
           graphics.QtCore.Qt.Key_3: 3,
           graphics.QtCore.Qt.Key_6: 4,
           graphics.QtCore.Qt.Key_9: 5,
           graphics.QtCore.Qt.Key_8: 6,
           graphics.QtCore.Qt.Key_7: 7,
           graphics.QtCore.Qt.Key_4: 8,
           }

character_identity = 0


class Status(object):
    """
    status: List of character status, including:
        0. vitality: Influence the health of character. Also influence the recovering speed of character's status.
        1. constitution: Influence the max injure of character. When character's injure point greater than max point,
            character's health become decrease. Also influence character's resistance to physical effect. Also
            influence character's max energy.
        2. endurance: Influence the endurance of character. Character's action and some skills will cost endurance.
            After endurance reaching zero, Character's some status becoming decreased.
        3. strength: Influence the max weight of weapons and items which characters can hold. Also influence the damage
            of characters' attack.
        4. agility: Influence the speed of character's action.
        5. intelligence: Influence the effect of character's skill. Also influence the time of learning a new skill.
        6. willpower: Influence the max sanity of character. When character's sanity reached the max point, character's
            are probably stunned. Also influence the max overflow value of character's endurance and source energy.
            Also influence the character's max energy.
    source: List of character's source power. Influence character's certain property and the effect of source alchemy.
    """
    def __init__(self):
        self.status = [10 for i in range(8)]
        self.source = [1 for i in range(5)]
        self.health = 0
        self.endure = 0
        self.energy = 0
        self.injure = 0
        self.sanity = 0

    def initialize(self, *args):
        assert len(args) == 13
        self.status = args[:8]
        self.source = args[8:]


class Effect(object):
    """
    Define the effect adding to character
    """
    def __init__(self, owner, state=None, status=Status(), period=Df.INF, count=Df.INF):
        self.status = status
        self.period = period
        self.count = count
        self.owner = owner
        self.state = None
        self.set_state(state)

    def set_state(self, new_state):
        if new_state is None:
            self.state = EffectDefault
        else:
            self.state = new_state


class EffectDefault(Effect):
    @staticmethod
    def max_health(conn):
        return 0

    @staticmethod
    def max_injure(conn):
        return 0

    @staticmethod
    def max_endure(conn):
        return 0

    @staticmethod
    def max_energy(conn):
        return 0

    @staticmethod
    def max_sanity(conn):
        return 0

    @staticmethod
    def attack_mult(conn, weapon_weight=0):
        return 0

    @staticmethod
    def attack_plus(conn, weapon_weight=0):
        return 0

    @staticmethod
    def dod_ratio(conn):
        return 0

    @staticmethod
    def hit_ratio(conn):
        return 0

    @staticmethod
    def attack_decr(conn):
        return 0

    @staticmethod
    def basic_speed(conn):
        return 0

    @staticmethod
    def pain_ratio(conn):
        return 0

    @staticmethod
    def obser_area(conn):
        return 0

    @staticmethod
    def con_ratio(conn):
        return 0

    @staticmethod
    def ale_ratio(conn):
        return 0

    @staticmethod
    def reco_health(conn):
        return 0

    @staticmethod
    def reco_injure(conn):
        return 0

    @staticmethod
    def reco_endure(conn):
        return 0

    @staticmethod
    def reco_energy(conn):
        return 0

    @staticmethod
    def reco_sanity(conn):
        return 0

    @staticmethod
    def limit_endure(conn):
        return 0

    @staticmethod
    def limit_energy(conn):
        return 0

    @staticmethod
    def limit_sanity(conn):
        return 0

    @staticmethod
    def speed_ratio(conn):
        return 0


class EffectDefend(EffectDefault):
    @staticmethod
    def attack_decr(conn):
        return 0.5


class CharStatus(Status):
    """
    The Status of characters (not weapons, armors, items, etc). Including function of basic status calculation.
    function:
        get_basic_time: the basic time that character's action cost. Every action takes multiples of this value.No less
            than 1.
        get_hold_weight: the max weight that character can hold by hand (or other part) and use it.
        get_bear_weight: the max weight that character can carry in bag or other thing.
    """
    def __init__(self):
        super(CharStatus, self).__init__()
        self.effects = []
        self.paralyse = False
        self.weapon_weight = 0
        self._count = 0

    def random_initialize(self, *args):
        assert len(args) == 13
        for index, element in enumerate(self.status):
            self.status[index] = random.randint(5, 5 + args[index])
        for index, element in enumerate(self.source):
            self.source[index] = args[8 + index]

    @property
    def cu_status(self):
        return_list = []
        for i, num in enumerate(self.status):
            result = num
            for effect in self.effects:
                result += effect.status.status[i]
            return_list.append(result)
        return return_list

    @property
    def cu_source(self):
        return_list = []
        for i, num in enumerate(self.source):
            result = num + 1
            for effect in self.effects:
                result += effect.status.source[i]
            return_list.append(result)
        return return_list

    def use(self, name):
        result = getattr(self, name)()
        for i in self.effects:
            result += getattr(i.state, name)(self)
        return max(1, result)

    def max_health(self):
        return self.cu_status[0] * self.cu_source[4] * 100 + 10

    def max_injure(self):
        return self.cu_status[1] * self.cu_source[3] * 10 + 10

    def max_endure(self):
        return self.cu_status[2] * self.cu_source[0] * 10 + 10

    def max_energy(self):
        return (self.cu_status[0] + self.cu_status[1]) * self.cu_source[0] * 10 + 10

    def max_sanity(self):
        return self.cu_status[6] * self.cu_source[2] * 10 + 10

    def attack_mult(self):
        return lg(self.cu_source[1]) + lg(self.weapon_weight) / 10.0

    def attack_plus(self):
        return (self.cu_status[3] - self.weapon_weight) * self.cu_source[1]

    def dod_ratio(self):
        return self.cu_status[4] * 2 + self.cu_status[7]

    def hit_ratio(self):
        return self.cu_status[4] + self.cu_status[7]

    def attack_decr(self):
        return min(self.cu_source[3] / 100.0, 0.9)

    def basic_speed(self):
        return int(max(10 - lg(self.cu_status[4]) - lg(self.cu_source[0]), 1) * self.speed_ratio())

    def pain_ratio(self):
        return self.cu_status[7] / (self.cu_status[6] + self.cu_status[1] * self.cu_source[3])

    def obser_area(self):
        return lg(self.cu_status[7]**2) + 1

    def con_ratio(self):
        return self.cu_status[4] + self.cu_status[6] + self.cu_status[7]

    def ale_ratio(self):
        return self.cu_status[6] + self.cu_status[7] * 2

    def reco_health(self):
        return self.cu_status[0] * self.cu_source[4] // 10

    def reco_injure(self):
        return self.cu_status[0] * self.cu_source[3] // 10

    def reco_endure(self):
        return self.cu_status[0] * self.cu_source[0] // 10

    def reco_energy(self):
        return -(self.cu_status[0] + self.cu_status[1] - self.cu_source[4]) // 10

    def reco_sanity(self):
        return self.cu_status[6]

    def limit_endure(self):
        return self.cu_status[6] * 5

    def limit_energy(self):
        return self.cu_status[6] * 5

    def limit_sanity(self):
        return self.cu_status[6] * 5

    def speed_ratio(self):
        if self.endure > self.use("max_endure"):
            return float(self.endure) / float(self.use("max_endure"))
        return 1.0

    def __repr__(self):
        return str(([ele for ele in self.cu_status], [ele for ele in self.cu_source]))

    @property
    def dead(self):
        if self.health > self.use("max_health"):
            return True
        else:
            return False

    @dead.setter
    def dead(self, value):
        if value:
            self.health = self.use("max_health") + 1
        else:
            self.health = 0

    @property
    def fail(self):
        if self.endure > self.use("max_endure"):
            overflow = self.endure - self.use("max_endure")
            check1 = random.randrange(overflow)
            check2 = random.randrange(self.use("limit_endure"))
            if check1 > check2:
                return True
        return False

    def paralyse_check(self):
        if self.paralyse:
            if not self.sanity:
                self.paralyse = False
        if self.sanity > self.use("max_sanity"):
            overflow = self.sanity - self.use("max_sanity")
            check1 = random.randrange(overflow)
            check2 = random.randrange(self.use("limit_sanity"))
            if check1 > check2:
                self.paralyse = True

    def natural_recover(self):
        ratio = 1.0
        if self.energy > self.use("max_energy"):
            overflow = self.energy - self.use("max_energy")
            ratio = 1.0 - float(overflow) / float(self.use("limit_energy"))
            if ratio < 0.0:
                return
        self.injure -= int(self.use("reco_injure") * ratio)
        self.endure -= int(self.use("reco_endure") * ratio)
        self.sanity -= int(self.use("reco_sanity") * ratio)
        self.energy -= int(self.use("reco_energy") * ratio)
        if self.injure < 0:
            self.injure = 0
        if self.endure < 0:
            self.endure = 0
        if self.sanity < 0:
            self.sanity = 0
        if self.energy < 0:
            self.energy = 0

    def update(self):
        self._count += 1
        if self._count > 20:
            self.natural_recover()
            self._count = 0
        self.paralyse_check()
        if self.injure > self.use("max_injure"):
            overflow = self.injure - self.use("max_injure")
            self.health += overflow
        for element in self.effects:
            assert isinstance(element, Effect)
            element.period -= 1
            if element.period < 0:
                self.effects.remove(element)

    def action(self):
        if self.injure > self.use("max_injure"):
            overflow = self.injure - self.use("max_injure")
            self.sanity += int(overflow * self.use("pain_ratio"))
        for element in self.effects:
            assert isinstance(element, Effect)
            element.count -= 1
            if element.count < 0:
                self.effects.remove(element)


class RigidBody(graphics.DrawObject):
    """
    移动时先将目标位置地图块的刚体参数赋值，再根据原先位置进行动画演算
    """
    def __init__(self, scene, tile, image, frames, centre_x=0.5, centre_y=1.0):
        super().__init__(image, frames, centre_x, centre_y)
        self.scene = scene
        self.tile = tile
        self.draw_image = image
        self.previous_tile = None
        self.setVisible(True)

        self.rigid_opacity = 0

        self.rigid_height = 1.0
        self.rigid_size = 1.0
        self.shadow = None
        self.mouse_on = False

    def save_type(self):
        return None

    def initialize(self, pos_x, pos_y):
        super().initialize(pos_x, pos_y)
        ratio = self.rigid_height * TILE_WIDTH / self.image_height
        self.image_height *= ratio
        self.image_width *= ratio
        if self.shadow is None:
            self.shadow = graphics.Shadow(self)
        self.setZValue(1 + self.tile.scene_pos_y)

    def move_to(self, next_tile, total_step=None):
        if next_tile is None:
            return False
        if next_tile.rigid_body is not None:
            return False
        if total_step is None:
            total_step = graphics.ANIMATION_FRAME
        if self.tile is not None:
            if self.isVisible():
                self.animation_move(next_tile.pos_x, next_tile.pos_y, total_step)
            else:
                self.setPos(next_tile.pos_x, next_tile.pos_y)
            self.tile.rigid_body = None
        self.tile = next_tile
        self.tile.rigid_body = self
        self.setZValue(1 + self.tile.scene_pos_y)
        return True

    def paint(self, painter, option, widget):
        if self.tile.visible:
            if self.mouse_on:
                self.next_opacity = 0.3
                self.mouse_on = False
            else:
                self.next_opacity = 1.0
        else:
            self.next_opacity = 0.01
        super().paint(painter, option, widget)


class Character(RigidBody):
    """
    Character:
    """
    def __init__(self, image_name, scene, tile, frames=None, centre_x=0.5, centre_y=1.0, action_time=0, identity=None):
        if frames is None:
            frames = [0]
        image = graphics.Resources.character_images[image_name[0]][image_name[1]]
        super(Character, self).__init__(scene, tile, image, frames, centre_x, centre_y)
        self.image_name = image_name
        self.status = CharStatus()
        self.action_time = action_time

        self.rigid_height = 1.5
        self.rigid_size = 1.0

        if identity is None:
            self.identity = character_identity
        else:
            self.identity = identity

    def paint(self, painter, option, widget):
        super().paint(painter, option, widget)
        self.next_opacity = min(self.next_opacity, self.tile.next_opacity)

    @property
    def sight_area(self):
        return 15

    # # check if the target block can be reached without obstacles
    def check_tile(self, target_x, target_y):
        distance = max(abs(target_x), abs(target_y))
        if distance < self.status.use("obser_area"):
            return distance, True
        for t in range(int(distance) + 1):
            dx = int(target_x / distance * t)
            dy = int(target_y / distance * t)
            tile = self.scene.get_tile_absolute(self.tile.scene_pos_x + dx, self.tile.scene_pos_y + dy)
            if (tile and isinstance(tile.rigid_body, RigidBody)
                    and (tile.rigid_body.rigid_opacity == 1
                         or (tile.rigid_body.rigid_opacity == 0 and tile.rigid_body.rigid_height > self.rigid_height))
                    and (dx != 0 or dy != 0) and (dx != target_x or dy != target_y)):
                return distance, False
        return distance, True

    def find_way(self, target_x, target_y):
        if not (-10 <= target_x < 10 and -10 < target_y < 10):
            return Pos.r_direction[(sgn(target_x), sgn(target_y))]
        map_data = [[-1 for i in range(20)] for j in range(20)]
        for dx, dy in double_range(0, 20, 0, 20):
            x, y = dx + self.tile.scene_pos_x - 10, dy + self.tile.scene_pos_y - 10
            if 0 <= x < self.scene.get_width() and 0 <= y < self.scene.get_height():
                if self.scene.get_tile_absolute(x, y).rigid_body:
                    map_data[dx][dy] = -1
                else:
                    map_data[dx][dy] = 0
            else:
                map_data[dx][dy] = -1
            map_data[target_x + 10][target_y + 10] = 0
        return Calculate.find_way(map_data, 10, 10,
                                  target_x + 10, target_y + 10)

    def death_process(self):
        self.tile.rigid_body = None
        self.scene.removeItem(self)
        self.scene.characters.remove(self)

    def update_game(self):
        # # every time update in the scene called this function in each character, including player
        self.status.update()
        if self.status.dead:
            self.death_process()
            self.scene.text_out("Some one dies like a dog")
    
    def move_next(self, direction, total_step=None, cost_time=10):
        if not direction:
            return
        dx, dy = Pos.direction[direction]
        self.move_to(self.scene.get_tile_absolute(self.tile.scene_pos_x + dx, self.tile.scene_pos_y + dy),
                     total_step)
        if direction in [1, 3, 5, 7]:
            self.action_time += cost_time * 3
        else:
            self.action_time += cost_time << 1

    # # true action in game

    # # action_move(director)
    def action_move(self, args):
        self.move_next(args[0], cost_time=self.status.use("basic_speed"))

    # # action_walk(director)
    def action_walk(self, args):
        self.move_next(args[0])

    # # action_dash(director)
    def action_dash(self, args):
        self.move_next(args[0], cost_time=self.status.use("basic_speed") >> 1)
        self.move_next(args[0], cost_time=self.status.use("basic_speed") >> 1)
        self.status.endure += 5
        self.status.energy += 1

    # # action_attack_normal(director)
    def action_attack_normal(self, args):
        self.action_time += self.status.use("basic_speed") << 1
        dx, dy = Pos.direction[args[0]]
        target = self.scene.get_tile_absolute(self.tile.scene_pos_x + dx, self.tile.scene_pos_y + dy)
        if isinstance(target, Character):
            damage = int((self.status.use("attack_plus") + 10) * self.status.use("attack_mult") *
                         (1 - min(0.9, target.status.use("attack_decr"))))
            target.status.injure += damage
        self.status.endure += 5
        self.status.energy += 1

    # # action_push(director, target_director)
    def action_push(self, args):
        dx, dy = Pos.direction[args[0]]
        target = self.scene.get_tile_absolute(self.tile.scene_pos_x + dx, self.tile.scene_pos_y + dy)
        self.action_walk([args[0]])
        if isinstance(target, Character):
            target.action_move([args[1]])

    # # after save_type must add the coordinate of character
    def save_type(self):
        return self.identity, self.status, self.frames, self.image_name, self.centre_x, self.centre_y

    @classmethod
    def load(cls, save, tile, scene, action_time=0):
        identity, status, frames, image_name, centre_x, centre_y = save
        result = cls(image_name, scene, tile, frames, centre_x, centre_y, action_time, identity)
        result.image_name = image_name
        result.frames = frames
        result.status = status
        return result


class NonePlayerMood(object):
    """

    """
    def __init__(self, character):
        super().__init__()
        self.character = character
        self.interact_moods = {}


class NonePlayer(Character):
    def __init__(self, image_name, scene, tile, frames=None, centre_x=0.5, centre_y=1.0, action_time=0, identity=None):
        super().__init__(image_name, scene, tile, frames, centre_x, centre_y, action_time, identity)
        self.ai_state = self.state_idle0
        self.visible_characters = []

    def auto_update(self, current_time):
        if self.action_time < current_time:
            self.visible_characters = []
            self.refresh_character()
            self.ai_state()

    def refresh_character(self):
        for dx, dy in double_range(
                -SIGHT_AREA, SIGHT_AREA + 1, -SIGHT_AREA, SIGHT_AREA + 1):
            tile = self.scene.get_tile_absolute(self.tile.scene_pos_x + dx, self.tile.scene_pos_y + dy)
            if tile and isinstance(tile.rigid_body, Character) and self.check_tile(dx, dy)[1]:
                self.visible_characters.append(tile.rigid_body)

    def state_wait0(self):
        # # npc stands still
        self.move_next(0)

    def state_idle0(self):
        # # npc move randomly
        direction = random.randrange(9)
        self.move_next(direction)

    
class Player(Character):
    def __init__(self, image_name, scene, tile, frames=None, centre_x=0.5, centre_y=1.0, action_time=0, identity=None):
        super().__init__(image_name, scene, tile, frames, centre_x, centre_y, action_time, identity)

    # #控制玩家动作，传入参数为动作类型（字符串），动作方向（可选）
    def control(self, action, args=[]):
        getattr(self, action)(args)

    def refresh(self):
        for tile in self.scene.get_all_tiles():
            tile.visible = False
            tile.next_opacity = 0.01
        for dx, dy in double_range(
                -SIGHT_AREA, SIGHT_AREA + 1, -SIGHT_AREA, SIGHT_AREA + 1):
            tile = self.scene.get_tile_absolute(self.tile.scene_pos_x + dx, self.tile.scene_pos_y + dy)
            if not tile:
                continue
            distance, visible = self.check_tile(dx, dy)
            tile.visible = visible
            if tile.visible:
                tile.setZValue(-1.1)
            else:
                tile.setZValue(-0.9)
            tile.next_opacity = min(1, visible + 0.01)
            if tile.rigid_body:
                tile.rigid_body.next_opacity = tile.next_opacity

    def update_game(self):
        super().update_game()


class Obstacle(RigidBody):
    def __init__(self, identity, image_key, scene, tile, image, frames=None, centre_x=0.5, centre_y=1.0):
        self.identity = identity
        self.image_key = image_key
        if frames is None:
            frames = [self.identity]
        super().__init__(scene, tile, image[image_key], frames, centre_x, centre_y)
        self.mouse_on = False

    @classmethod
    def create(
            cls, identity, image_key, scene, tile, image, rigid_height=1.0, rigid_size=1.0, rigid_opacity=0,
            centre_x=0.5, centre_y=1.0):
        result = cls(identity, image_key, scene, tile, image, centre_x=centre_x, centre_y=centre_y)
        result.rigid_height = rigid_height
        result.rigid_size = rigid_size
        result.rigid_opacity = rigid_opacity
        return result

    def save_type(self):
        return (self.identity, self.image_key, self.rigid_height, self.rigid_size, self.rigid_opacity,
               self.centre_x, self.centre_y)

    @classmethod
    def load(
            cls, save_type, scene, tile, image):
        identity, image_key, rigid_height, rigid_size, rigid_opacity, centre_x, centre_y = save_type
        return cls.create(
            identity, image_key, scene, tile, image, rigid_height, rigid_size, rigid_opacity, centre_x, centre_y)


class GameItem(object):
    def __init__(self):
        pass


if __name__ == "__main__":
    pass
