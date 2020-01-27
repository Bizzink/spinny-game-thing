import pyglet as pgl
from .rect import Rect


class Tile:
    def __init__(self, pos, rot, image, hitbox, batch=None, group=None):
        self.x = pos[0]
        self.y = pos[1]
        self.rot = rot

        self.hitbox = Rect(pos, hitbox)

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

    def debug_enable(self, batch, group=None):
        """enable drawing of hitbox"""
        self.hitbox.debug_enable(batch, group)

    def debug_disable(self):
        """delete debug visuals from batch"""
        self.hitbox.debug_disable()

    def debug_toggle(self, batch, group=None):
        """toggle debug rendering on or off"""
        if self._debug:
            self._debug = False
            self.debug_disable()
        else:
            self._debug = True
            self.debug_enable(batch, group)


class TileAll(Tile):
    def __init__(self, pos, rot, batch=None, group=None):
        super().__init__(pos, rot, "tile_all.png", [[-20, -20], [-20, 20], [20, 20], [20, -20]], batch=batch, group=group)


class TilePipe(Tile):
    def __init__(self, pos, rot, batch=None, group=None):
        super().__init__(pos, rot, "tile_pipe.png", [[-25, 20], [-25, -20], [25, -20], [25, 20]], batch=batch, group=group)


class TileEnd(Tile):
    def __init__(self, pos, rot, batch=None, group=None):
        super().__init__(pos, rot, "tile_end.png", [[-20, 20], [-20, -20], [25, -20], [25, 20]], batch=batch, group=group)
