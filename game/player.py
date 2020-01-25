import pyglet as pgl
from pyglet.window import key
from math import sqrt, atan, cos, sin, pi


class Player:
    def __init__(self, pos, batch=None):
        self.x = pos[0]
        self.y = pos[1]

        self._acc = 50
        self._max_vel = 500
        self._max_x_val = 450
        self._max_y_val = 800
        self._drag = 0.995
        self._rot_acc = 0.8
        self._max_rot_vel = 8
        self._rot_drag = 0.95

        self.vel_x = 0
        self.vel_y = 0
        self.rot = 0
        self.vel_rot = 0

        self.key_handler = key.KeyStateHandler()

        #  Image / sprite setup
        self._image = pgl.resource.image("player.png")
        self._image.center_x = self._image.width // 2
        self._image.center_y = self._image.height // 2
        self._image.anchor_x = self._image.width // 2
        self._image.anchor_y = self._image.height // 2
        self._sprite = pgl.sprite.Sprite(img=self._image, x=self.x, y=self.y, batch=batch)
        self._sprite.scale = 0.1

    def delete(self):
        self._sprite.delete()

    def update(self, dt):
        #  key handling
        if self.key_handler[key.W]:
            self.__acc_relative__(self._acc, 0)
        if self.key_handler[key.S]:
            self.__acc_relative__(-self._acc, 0)
        if self.key_handler[key.A]:
            self.__acc_rot__(-self._rot_acc)
        if self.key_handler[key.D]:
            self.__acc_rot__(self._rot_acc)

        #  physics update
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt
        self.rot += self.vel_rot
        self.__drag__()

        #  sprite update
        self._sprite.x = self.x
        self._sprite.y = self.y
        self._sprite.rotation = self.rot

    def debug_draw(self):
        """draw rotation and velocity vector for debug"""
        pgl.graphics.draw(2, pgl.gl.GL_LINES,
                          ('v2f', (self.x, self.y, self.x + self.vel_x * 0.5, self.y + self.vel_y * 0.5)),
                          ('c3B', (255, 0, 0, 100, 0, 0)))

        pgl.graphics.draw(2, pgl.gl.GL_LINES, ('v2f', (
            self.x, self.y, self.x + (cos((self.rot - 90) * pi / 180) * 100),
            self.y + (sin((self.rot - 90) * pi / 180) * -100))), ('c3B', (0, 255, 0, 0, 100, 0)))

    def acc_absolute(self, x, y):
        """accelerate absolute motion of player"""
        self.vel_x += x
        self.vel_y += y

        self.__limit_velocity__(mode = 'absolute')

    def __limit_velocity__(self, mode='absolute'):
        """limit velocity to max_vel"""
        #  velocity per direction
        if mode == 'absolute':
            if self.vel_x > self._max_x_val:
                self.vel_x = self._max_x_val
            if self.vel_y > self._max_y_val:
                self.vel_y = self._max_y_val
            if self.vel_x < -self._max_x_val:
                self.vel_x = -self._max_x_val
            if self.vel_y < -self._max_y_val:
                self.vel_y = -self._max_y_val

        #  velocity vector length max
        if mode == 'total':
            vel = sqrt(self.vel_x ** 2 + self.vel_y ** 2)

            if vel > self._max_vel:
                if self.vel_x == 0:
                    vel_ang = -pi / 2
                else:
                    vel_ang = atan(self.vel_y / self.vel_x)

                #  add 180 degrees if vel_x is negative
                if self.vel_x < 0:
                    vel_ang += pi

                self.vel_x = cos(vel_ang) * self._max_vel
                self.vel_y = sin(vel_ang) * self._max_vel

    def __acc_relative__(self, forward_back, left_right):
        """accelerate motion of player relative to direction it is facing, cap at max_vel"""
        #  forward / backward acceleration
        self.vel_x += cos((self.rot + 90) * pi / 180) * -forward_back
        self.vel_y += sin((self.rot + 90) * pi / 180) * forward_back
        #  left / right acceleration
        self.vel_x += cos(self.rot * pi / 180) * left_right
        self.vel_y += sin(self.rot * pi / 180) * -left_right

        self.__limit_velocity__()

    def __acc_rot__(self, a):
        """accelerate rotation of player, cap at max_rot"""
        self.vel_rot += a

        #  limit rotational velocity to max_rot_val
        if self.vel_rot > self._max_rot_vel: self.vel_rot = self._max_rot_vel
        if self.vel_rot < -self._max_rot_vel: self.vel_rot = -self._max_rot_vel

    def __drag__(self):
        """apply drag to motion of player, set motion to 0 if it is too low"""
        self.vel_x *= self._drag
        self.vel_y *= self._drag
        self.vel_rot *= self._rot_drag

        if -0.1 < self.vel_x < 0.1: self.vel_x = 0
        if -0.1 < self.vel_y < 0.1: self.vel_y = 0
        if -0.1 < self.vel_rot < 0.1: self.vel_rot = 0
