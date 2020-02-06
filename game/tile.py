import pyglet as pgl
from .rect import Rect


class Tile:
    def __init__(self, pos, rot, style_id, shape_id, colour = (255, 255, 255), outline = False, outline_colour = (255, 255, 255), batch=None, group=None):
        self.x = pos[0]
        self.y = pos[1]
        self.rot = rot

        self.shape = shape_id
        self.style = style_id

        self.colour = colour

        self.has_outline = outline
        self.outline_colour = outline_colour

        if shape_id == 1:
            hitbox = [[-20, -20], [-20, 20], [20, 20], [20, -20]]
        elif shape_id == 2:
            hitbox = [[-20, 20], [-20, -20], [25, -20], [25, 20]]
        elif shape_id == 3:
            hitbox = [[-25, 20], [-25, -20], [25, -20], [25, 20]]
        elif shape_id == 4:
            hitbox = []
        elif shape_id == 5:
            hitbox = []
        elif shape_id == 6:
            hitbox = []

        self.hitbox = Rect(pos, hitbox)
        self.hitbox.update(self.x, self.y, self.rot)

        self.friction = 0.95

        #  sprite setup
        self._image = pgl.resource.image("tile_{}_{}.png".format(self.style, self.shape))
        self._image.center_x = self._image.width // 2
        self._image.center_y = self._image.height // 2
        self._image.anchor_x = self._image.width // 2
        self._image.anchor_y = self._image.height // 2
        self._sprite = pgl.sprite.Sprite(img=self._image, x=self.x, y=self.y, batch=batch, group=group)
        self._sprite.rotation = self.rot
        self._sprite.scale = 0.1
        self._sprite.color = self.colour

        # TODO: outline
        self._outline_image = None

        self._debug = False

    def debug_enable(self, batch, group=None):
        """enable drawing of hitbox"""
        self._debug = True
        self.hitbox.debug_enable(batch, group)

    def debug_disable(self):
        """delete debug visuals from batch"""
        self._debug = False
        self.hitbox.debug_disable()

    def set_rot(self, angle):
        self.rot = angle

    def set_colour(self, colour):
        print(colour)
        self.colour = colour
        self._sprite.color = colour

    def set_outline_colour(self, colour):
        self.outline_colour = colour

    def enable_outline(self):
        self.has_outline = True
        self._outline_image = None

    def disable_outline(self):
        self.has_outline = False
        self._outline_image = None

    def delete(self):
        self._sprite.delete()
        del self
