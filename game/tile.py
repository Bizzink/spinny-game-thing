import pyglet as pgl


class Tile:
    def __init__(self, pos, image, batch = None):
        self.x = pos[0]
        self.y = pos[1]

        self._image = pgl.resource.image(image)
        self._image.center_x = self._image.width // 2
        self._image.center_y = self._image.height // 2
        self._image.anchor_x = self._image.width // 2
        self._image.anchor_y = self._image.height // 2
        self._sprite = pgl.sprite.Sprite(img = self._image, x = self.x, y = self.y, batch = batch)
        self._sprite.scale = 0.1
