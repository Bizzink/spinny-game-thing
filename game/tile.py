import pyglet as pgl


class Tile:
    def __init__(self, pos, rot, image, hitbox, batch=None, group=None):
        self.x = pos[0]
        self.y = pos[1]
        self.rot = rot

        self.hitbox = []
        #  Hitbox co-ords are relative to pos (center of tile), convert to actual co-ords
        for i in range(len(hitbox)):
            if i % 2 == 1:  # y co-ords
                self.hitbox.append(hitbox[i] + self.y)
            else:  # x co-ords
                self.hitbox.append(hitbox[i] + self.x)

        print(self.hitbox)

        self.area = self.__get__area__()

        #  sprite setup
        self._image = pgl.resource.image(image)
        self._image.center_x = self._image.width // 2
        self._image.center_y = self._image.height // 2
        self._image.anchor_x = self._image.width // 2
        self._image.anchor_y = self._image.height // 2
        self._sprite = pgl.sprite.Sprite(img=self._image, x=self.x, y=self.y, batch=batch, group=group)
        self._sprite.rotation = self.rot
        self._sprite.scale = 0.1

        self._debug = False
        self._debug_vertex_list = None

    def debug_enable(self, batch, group=None):
        """enable drawing of hitbox"""
        # colour = []
        # for _ in range(len(self.hitbox) // 2):
        #    colour.extend([50, 50, 255])

        # self._debug_vertex_list = batch.add(len(self.hitbox) // 2, pgl.gl.GL_LINE_LOOP, group, ('v2f', self.hitbox), ('c3B', colour))
        """due to a quirk in the way line_loop (and some other primitives) are rendered, this ^ doesn't work properly
        so this is a workaround."""
        self._debug_vertex_list = []

        for i in range(len(self.hitbox) // 2):
            vertex = batch.add(2, pgl.gl.GL_LINES, group, ('v2f', (
                self.hitbox[(i * 2) - 2], self.hitbox[(i * 2) - 1], self.hitbox[(i * 2)], self.hitbox[(i * 2) + 1])),
                               ('c3B', (50, 50, 255, 50, 50, 255)))
            self._debug_vertex_list.append(vertex)

    def debug_disable(self):
        # self._debug_vertex_list.delete()

        for vertex in self._debug_vertex_list:
            vertex.delete()

        self._debug_vertex_list = None

    def debug_toggle(self, batch, group=None):
        if self._debug:
            self._debug = False
            self.debug_disable()
        else:
            self._debug = True
            self.debug_enable(batch, group)

    def __get__area__(self):
        """get area of hitbox.
        algorithm from https://www.mathopenref.com/coordpolygonarea2.html"""
        x, y = [], []

        for i in range(len(self.hitbox)):
            if i % 2 == 1:  # x co-ord
                x.append(self.hitbox[i])
            else:  # y co-ord
                y.append(self.hitbox[i])

        points = len(self.hitbox) // 2

        area = 0
        j = points - 1

        for i in range(points):
            area += (x[j] + x[i]) * (y[j] - y[i])
            j = i  # j is previous vertex to i

        return area / 2


class TileAll(Tile):
    def __init__(self, pos, rot, batch=None, group=None):
        super().__init__(pos, rot, "tile_all.png", (-20, -20, -20, 20, 20, 20, 20, -20), batch=batch, group=group)


class TilePipe(Tile):
    def __init__(self, pos, rot, batch=None, group=None):
        super().__init__(pos, rot, "tile_pipe.png", (-25, 20, -25, -20, 25, -20, 25, 20), batch=batch, group=group)


class TileEnd(Tile):
    def __init__(self, pos, rot, batch=None, group=None):
        super().__init__(pos, rot, "tile_end.png", (-20, 20, -20, -20, 25, -20, 25, 20), batch=batch, group=group)
