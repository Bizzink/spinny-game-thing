import pyglet as pgl
from pyglet.window import key
from math import sqrt, atan, cos, sin, pi


class Player:
    def __init__(self, pos, hitbox, batch=None, group=None):
        self.x = pos[0]
        self.y = pos[1]

        self._hitbox = [[point[0] + self.x, point[1] + self.y] for point in hitbox]
        self._hitbox_ref = hitbox
        self._checkbox = None
        self.__update_checkbox__()

        self._acc = 50
        self._max_vel = 500
        self._max_x_val = 450
        self._max_y_val = 800
        self._drag = 0.995
        self._rot_acc = 30
        self._max_rot_vel = 300
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
        self._sprite = pgl.sprite.Sprite(img=self._image, x=self.x, y=self.y, batch=batch, group=group)
        self._sprite.scale = 0.1

        self._debug = False
        self._debug_direction = None
        self._debug_velocity = None
        self._debug_vertex_list = None

    def delete(self):
        self._sprite.delete()
        self.debug_disable()

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
        self.rot += self.vel_rot * dt
        self.__drag__()

        #  sprite update
        self._sprite.x = self.x
        self._sprite.y = self.y
        self._sprite.rotation = self.rot

        self.__update_hitbox__()
        self.__update_checkbox__()

        #  debug updating
        if self._debug:
            self._debug_direction.vertices = [self.x, self.y, self.x + (cos((self.rot - 90) * pi / 180) * 100),
                                              self.y + (sin((self.rot - 90) * pi / 180) * -100)]
            self._debug_velocity.vertices = [self.x, self.y, self.x + self.vel_x * 0.5, self.y + self.vel_y * 0.5]

            for i in range(len(self._hitbox)):
                self._debug_vertex_list[i].vertices = [self._hitbox[i - 1][0], self._hitbox[i - 1][1],
                                                       self._hitbox[i][0], self._hitbox[i][1]]

            for i in range(len(self._checkbox)):
                j = i + len(self._hitbox)
                self._debug_vertex_list[j].vertices = [self._checkbox[i - 1][0], self._checkbox[i - 1][1],
                                                       self._checkbox[i][0], self._checkbox[i][1]]

    def debug_enable(self, batch, group=None):
        """enable drawing of rotation and velocity vectors"""
        self._debug = True

        self._debug_direction = batch.add(2, pgl.gl.GL_LINES, group, ('v2f/stream', (
            self.x, self.y, self.x + (cos((self.rot - 90) * pi / 180) * 100),
            self.y + (sin((self.rot - 90) * pi / 180) * -100))), ('c3B/static', (0, 255, 0, 0, 100, 0)))

        self._debug_velocity = batch.add(2, pgl.gl.GL_LINES, group, ('v2f/stream', (
            self.x, self.y, self.x + self.vel_x * 0.5, self.y + self.vel_y * 0.5)),
                                         ('c3B/static', (255, 0, 0, 100, 0, 0)))

        #  Same code from tile class to draw hitbox
        self._debug_vertex_list = []

        for i in range(len(self._hitbox)):
            vertex = batch.add(2, pgl.gl.GL_LINES, group, ('v2f', (self._hitbox[i - 1][0],
                                                                   self._hitbox[i - 1][1],
                                                                   self._hitbox[i][0],
                                                                   self._hitbox[i][1])),
                               ('c3B', (50, 50, 255, 50, 50, 255)))
            self._debug_vertex_list.append(vertex)

        for i in range(len(self._checkbox)):
            vertex = batch.add(2, pgl.gl.GL_LINES, group, ('v2f', ([self._checkbox[i - 1][0],
                                                                    self._checkbox[i - 1][1],
                                                                    self._checkbox[i][0],
                                                                    self._checkbox[i][1]])),
                               ('c3B', (50, 255, 255, 50, 255, 255)))
            self._debug_vertex_list.append(vertex)

    def debug_disable(self):
        """remove debug visuals from batch"""
        self._debug = False

        self._debug_direction.delete()
        self._debug_velocity.delete()

        for vertex in self._debug_vertex_list:
            vertex.delete()

    def debug_toggle(self, batch, group):
        """toggle debug on or off"""
        if self._debug:
            self.debug_disable()
        else:
            self.debug_enable(batch, group)

    def acc_absolute(self, x, y):
        """accelerate absolute motion of player"""
        self.vel_x += x
        self.vel_y += y

        self.__limit_velocity__(mode='absolute')

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

    def __update_hitbox__(self):
        """rotate hitbox points around origin
        code from https://stackoverflow.com/questions/2259476/rotating-a-point-about-another-point-2d"""
        points = [point.copy() for point in self._hitbox_ref.copy()]

        #  for some reason, self.rot needs to be negative, not sure why
        c, s = cos(-self.rot * pi / 180), sin(-self.rot * pi / 180)

        self._hitbox = [[c * point[0] - s * point[1] + self.x, s * point[0] + c * point[1] + self.y] for point in
                        points]

    def __update_checkbox__(self):
        """update checkbox (bounding box of hitbox)"""
        hitbox_x = [point[0] for point in self._hitbox]
        hitbox_y = [point[1] for point in self._hitbox]

        min_x = min(hitbox_x)
        max_x = max(hitbox_x)
        min_y = min(hitbox_y)
        max_y = max(hitbox_y)

        self._checkbox = [[min_x, min_y], [min_x, max_y], [max_x, max_y], [max_x, min_y]]
