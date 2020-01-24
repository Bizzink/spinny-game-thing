import pyglet as pgl


class Player:
    def __init__(self, pos, batch = None):
        self.x = pos[0]
        self.y = pos[1]
        self.vel_x = 0
        self.vel_y = 0
        self.rot = 0
        self.vel_rot = 0

        self._image = pgl.resource.image("player.png")
        self.__center_image__()
        self._sprite = pgl.sprite.Sprite(img = self._image, x = self.x, y = self.y, batch = batch)
        self._sprite.scale = 0.1

    def __center_image__(self):
        """possibly redundant, could move to init"""
        self._image.center_x = self._image.width // 2
        self._image.center_y = self._image.height // 2

    def draw(self):
        self._sprite.draw()

    def update(self, dt):
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt
        self.rot += self.vel_rot

        self._sprite.x = self.x
        self._sprite.y = self.y
        self._sprite.rotation = self.rot

    def acc_pos(self, x, y):
        self.vel_x += x
        self.vel_y += y

    def acc_rot(self, a):
        self.vel_rot += a
