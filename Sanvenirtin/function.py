#!usr/bin/python3
# -*-coding: utf-8 -*-

import pickle


class Define(object):
    INF = float("inf")


def sgn(num):
    if num > 0:
        return 1
    elif num < 0:
        return -1
    else:
        return 0


def save_byte(obj, file_path):
    with open(file_path, "wb") as f:
        pickle.dump(obj, f)


def load_byte(file_path):
    try:
        with open(file_path, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return False


def double_range(*args):
    if len(args) == 2:
        for i in range(args[0]):
            for j in range(args[1]):
                yield (i, j)
    elif len(args) == 4:
        for i in range(args[0], args[1]):
            for j in range(args[2], args[3]):
                yield (i, j)
    elif len(args) == 6:
        for i in range(args[0], args[1], args[2]):
            for j in range(args[3], args[4], args[5]):
                yield (i, j)
    else:
        raise TypeError("double_range expected 2 or 4 or 6 arguments, got %d" % len(args))


def log10(num):
    return len(str(int(num)))


class Pos(object):
    """
    Pos Object -- deal with position
    """
    direction = [(0, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0)]
    r_direction = {(0, 0): 0, (-1, 1): 1, (0, 1): 2,
                   (1, 1): 3, (1, 0): 4, (1, -1): 5,
                   (0, -1): 6, (-1, -1): 7, (-1, 0): 8}

    def __init__(self, x, y, width=Define.INF, height=Define.INF):
        self._x, self._y = None, None
        self.width = width
        self.height = height
        self.x, self.y = x, y

    def __add__(self, other):
        assert isinstance(other, tuple), "Pos object can only add tuple"
        return Pos(self.x + other[0], self.y + other[1], self.width, self.height)

    def __eq__(self, other):
        if (self.x, self.y, self.width, self.height) == (other.x, other.y, other.width, other.height):
            return True
        else:
            return False

    def area(self):
        for dx, dy in Pos.direction:
            yield self.limit_x(dx + self.x), self.limit_y(dy + self.y)

    def limit_x(self, arg):
        if arg >= self.width:
            arg -= self.width
        elif arg < 0:
            arg += self.width
        return arg

    def limit_y(self, arg):
        if arg >= self.height:
            arg -= self.height
        elif arg < 0:
            arg += self.height
        return arg

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, arg):
        self._x = self.limit_x(arg)

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, arg):
        self._y = self.limit_y(arg)

    @staticmethod
    def get_direction(index):
        return Pos.direction[index]

    @staticmethod
    def get_direction_index(dx, dy):
        return Pos.direction.index((dx, dy))


class Calculate(object):
    """
    Calculate Object -- including some calculation function
    """
    @staticmethod
    def find_way_area(x, y):
        for ele in [(-1, -1, 3), (0, -1, 2), (1, -1, 3), (1, 0, 2),
                    (1, 1, 3), (0, 1, 2), (-1, 1, 3), (-1, 0 ,2)]:
            yield x + ele[0], y + ele[1], ele[2]

    # # using A* algorithm
    @staticmethod
    def find_way(map_data, current_x, current_y, target_x, target_y):
        # # map_data: 0 means no obstacle, >0 means certain cost obstacle(2 is one tiles cost),
        #  -1 means obstacle cannot pass
        # # do_data: A star point data, a dict of parent, G, H
        # # return: if found return next direction, else return 0
        assert isinstance(map_data, list)
        width = len(map_data)
        height = len(map_data[0])
        do_data = [[{"X": x, "Y": y, "H": 2 * (abs(target_x - x) + abs(target_y - y)), "G": 0, "P": None}
                    for y in range(height)] for x in range(width)]
        open_list = [do_data[current_x][current_y]]
        close_list = []
        current_tile = do_data[current_x][current_y]
        while open_list and (do_data[target_x][target_y] is not current_tile):
            current_tile = None
            for ele in open_list:
                if not current_tile or ele["H"] + ele["G"] < current_tile["H"] + current_tile["G"]:
                    current_tile = ele
            try:
                open_list.remove(current_tile)
            except ValueError:
                print(open_list)
                print(current_tile)
                raise
            close_list.append(current_tile)
            for x, y, d in Calculate.find_way_area(current_tile["X"], current_tile["Y"]):
                if 0 <= x < width and 0 <= y < height:
                    if do_data[x][y] in close_list or map_data[x][y] < 0:
                        continue
                    elif do_data[x][y] not in open_list:
                        open_list.append(do_data[x][y])
                        do_data[x][y]["G"] = d + current_tile["G"]
                        do_data[x][y]["P"] = current_tile
                    else:
                        if d + current_tile["G"] < do_data[x][y]["G"]:
                            do_data[x][y]["G"] = d + current_tile["G"]
                            do_data[x][y]["P"] = current_tile

        if open_list:
            try:
                while current_tile["P"] and current_tile["P"] is not do_data[current_x][current_y]:
                    current_tile = current_tile["P"]
                return Pos.r_direction[(current_tile["X"] - current_x, current_tile["Y"] - current_y)]
            except TypeError:
                print(current_tile)
                raise
        else:
            return 0

