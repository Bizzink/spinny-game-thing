import pyglet as pgl


class Player:
    def __init__(self, pos):
        self._image = pgl.resource.image("player.png")
        self.__center_image__()
        self._pos = pos

        self._sprite = pgl.sprite.Sprite(img = self._image, x = self._pos[0], y = self._pos[1])
        self._sprite.scale = 0.1

    def __center_image__(self):
        self._image.center_x = self._image.width // 2
        self._image.center_y = self._image.height // 2

    def draw(self):
        self._sprite.draw()
