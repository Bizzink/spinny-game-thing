import pyglet as pgl
from pyglet.window import key
from math import sqrt, atan, cos, sin, pi


class Player:
    def __init__(self, pos, batch=None):
        self.x = pos[0]
        self.y = pos[1]

        self.vel_x = 0
        self.vel_y = 0
        self._max_vel = 150

        self._accel = 1
        self._drag = 0.95

        self.rot = 0
        self.vel_rot = 0
        self._max_rot = 2

        self.key_handler = key.KeyStateHandler()

        #  Image / sprite setup
        self._image = pgl.resource.image("player.png")
        self._image.center_x = self._image.width // 2
        self._image.center_y = self._image.height // 2
        self._image.anchor_x = self._image.width // 2
        self._image.anchor_y = self._image.height // 2
        self._sprite = pgl.sprite.Sprite(img=self._image, x=self.x, y=self.y, batch=batch)
        self._sprite.scale = 0.1

    def draw(self):
        self._sprite.draw()

    def update(self, dt):
        if self.key_handler[key.W]:
            self.__acc_relative__(10, 0)
        if self.key_handler[key.S]:
            self.__acc_relative__(-10, 0)

        if self.key_handler[key.A]:
            self.__acc_relative__(0, -10)
        if self.key_handler[key.D]:
            self.__acc_relative__(0, 10)

        if self.key_handler[key.LEFT]:
            self.__acc_rot__(-0.2)
        if self.key_handler[key.RIGHT]:
            self.__acc_rot__(0.2)

        self.x += self.vel_x * dt
        self.y += self.vel_y * dt
        self.rot += self.vel_rot

        self._sprite.x = self.x
        self._sprite.y = self.y
        self._sprite.rotation = self.rot

        self.__drag__()

    def acc_absolute(self, x, y):
        """accelerate absolute motion of player, cap at max_vel"""
        self.vel_x += x
        self.vel_y += y

        if self.vel_y > self._max_vel: self.vel_y = self._max_vel
        if self.vel_y < -self._max_vel: self.vel_y = -self._max_vel

    def __acc_relative__(self, forward_back, left_right):
        """accelerate motion of player relative to direction it is facing, cap at max_vel"""
        self.vel_x += cos((self.rot + 90) * pi / 180) * -forward_back * self._accel
        self.vel_y += sin((self.rot + 90) * pi / 180) * forward_back * self._accel

        self.vel_x += cos(self.rot * pi / 180) * left_right * self._accel
        self.vel_y += sin(self.rot * pi / 180) * -left_right * self._accel

        vel = sqrt(self.vel_x ** 2 + self.vel_y ** 2)
        if vel > self._max_vel:
            vel_ang = atan(self.vel_y / self.vel_x)

            if self.vel_x < 0:
                vel_ang += pi

            self.vel_x = cos(vel_ang) * self._max_vel
            self.vel_y = sin(vel_ang) * self._max_vel

    def __acc_rot__(self, a):
        """accelerate rotation of player, cap at max_rot"""
        self.vel_rot += a

        if self.vel_rot > self._max_rot: self.vel_rot = self._max_rot
        if self.vel_rot < -self._max_rot: self.vel_rot = -self._max_rot

    def __drag__(self):
        """apply drag to motion of player, set motion to 0 if it is too low"""
        self.vel_x *= self._drag
        self.vel_y *= self._drag
        self.vel_rot *= self._drag

        if -0.1 < self.vel_x < 0.1: self.vel_x = 0

        if -0.1 < self.vel_y < 0.1: self.vel_y = 0

        if -0.1 < self.vel_rot < 0.1: self.vel_rot = 0
