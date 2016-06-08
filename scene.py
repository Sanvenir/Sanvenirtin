from random import randrange
from function import double_range, save_byte, load_byte
LOCAL_WIDTH = 100
LOCAL_HEIGHT = 100
GLOBAL_WIDTH = 500
GLOBAL_HEIGHT = 500
INF = float("inf")


class Pos(object):
    """
    Pos Object -- deal with position
    """
    direction = [(0, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0)]

    def __init__(self, x, y, width=INF, height=INF):
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

    def area(self, dx, dy):
        for x, y in Pos.direction:
            yield self.limit_x(x), self.limit_y(y)

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
        self._contents = None

    def _new(self, width, height, content=None):
        self._width = width
        self._height = height
        self._contents = [[content for y in range(height)] for x in range(width)]

    def __getitem__(self, index):
        assert isinstance(self._contents, list), "content not set or incorrect!"
        assert isinstance(self._contents[index], list), "content not set or incorrect!"
        return self._contents[index]

    def random_create(self, *content_types):
        for (x, y) in double_range(self.get_width, self.get_height):
                self._contents[x][y] = content_types[randrange(len(content_types))]

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
            self._width, self._height, self._contents = result
            return True
        else:
            return False

    def saving(self):
        assert self._contents, "Contents not initialize!"
        save_byte((self.get_width, self.get_height, self._contents), self.file_path)


class LocalMap(SavingMaps):
    """
    LocalMap object -- maps where rigidbodys and items locating; If its content is none, the tile there remain blank;
    function:
        new_init: creating a new map;
        load_init: creating map from file;
        save: saving map to file;
    class property:
        identity: the identity of next new created map, using for saving and loading;
    """
    _identity = 0

    def __init__(self):
        super(LocalMap, self).__init__()
        self.identity = LocalMap._identity
        self.file_path = "sav//m%08d.dat" % self.identity
        LocalMap._identity += 1

    def install(self, width, height):
        if self.load_init():
            return True
        else:
            self.new_init(width, height)
            return False

    def uninstall(self):
        self.saving()
        self._contents = None


class GlobalMap(SavingMaps):
    """
    GlobalMap object -- map contain the whole world; Including normal local map;
    """
    def __init__(self):
        super(GlobalMap, self).__init__()
        self.file_path = "sav//map.dat"
        if not self.load_init():
            self.new_init(GLOBAL_WIDTH, GLOBAL_HEIGHT, LocalMap())
        self.saving()


class Scene(object):
    """
    Scene object -- contain a GlobalMap and temporary 3 * 3 LocalMaps
    """
    def __init__(self):
        super(Scene, self).__init__()
        self.global_map = GlobalMap()
        self.pos = None
        self._contents = []

    def uninstall(self):
        for i in self._contents:
            assert isinstance(i, LocalMap)
            i.uninstall()
        self._contents = []

    def set_pos(self, pos_x, pos_y):
        self.pos = Pos(pos_x, pos_y, self.global_map.get_width, self.global_map.get_height)
        old_maps = self._contents.copy()
        self._contents = [self.global_map[x][y] for (x, y) in self.pos.area(1, 1)]
        for local_map in self._contents:
            if local_map not in old_maps:
                local_map.install(LOCAL_WIDTH, LOCAL_HEIGHT)
        for local_map in old_maps:
            if local_map and local_map not in self._contents:
                local_map.uninstall()

    def set_map(self, local_map):
        if self._contents:
            self.uninstall()
        self._contents = [local_map] + [None for i in range(8)]

    def get_tile(self, x, y):
        if(0 <= x <)



if __name__ == "__main__":
    scene = Scene()
    scene.set_pos(10, 10)
    scene.set_pos(30, 30)

