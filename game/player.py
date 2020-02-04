import pyglet as pgl
from pyglet.window import key
from math import sqrt, atan2, cos, sin, pi
from .rect import Rect
from .particle import PointEmitter


class Player:
    def __init__(self, pos, batch=None, group=None):
        self.x = pos[0]
        self.y = pos[1]

        self.hitbox = Rect(pos, [[-5, -15], [-5, 15], [5, 15], [5, -15]])

        self._acc = 50
        self._max_vel = 500
        self._max_x_val = 450
        self._max_y_val = 800
        self._drag = 0.995
        self._rot_acc = 30
        self._max_rot_vel = 300
        self._rot_drag = 0.97

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

        self.smoke_particles = PointEmitter((self.x, self.y), direction = self.rot, max_particles = 20, size = 5, size_rand = 50, vel = 300, vel_rand = 2, rot_vel_rand = 100, spread = 50, emit_speed = 50, lifetime = 0.15, lifetime_rand = 0.1, batch = batch, group = group)
        self._rects_in_range = []

        self._debug = False
        self._debug_direction = None
        self._debug_velocity = None

    def delete(self):
        self._sprite.delete()
        self.debug_disable()
        self.hitbox.delete()
        self.smoke_particles.delete()
        del self

    def update(self, dt):
        self.smoke_particles.set_intensity(max_particles = 0)
        #  key handling
        if self.key_handler[key.W]:
            self.accelerate(0, self._acc, mode = "relative")
            self.smoke_particles.set_intensity(max_particles = 20)
        if self.key_handler[key.S]:
            self.accelerate(0, -self._acc, mode = "relative")
        if self.key_handler[key.A]:
            self.__acc_rot__(-self._rot_acc)
        if self.key_handler[key.D]:
            self.__acc_rot__(self._rot_acc)

        for rect in self._rects_in_range:
            self.__contact__(rect)

        #  physics update
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt
        self.rot += self.vel_rot * dt
        self.__drag__()

        while self.rot > 360:
            self.rot -= 360

        while self.rot < -360:
            self.rot += 360

        self.hitbox.update(self.x, self.y, self.rot)
        self.smoke_particles.set_pos(self.x, self.y, direction = self.rot + 90)
        self.smoke_particles.update(dt)

        #  sprite update
        self._sprite.x = self.x
        self._sprite.y = self.y
        self._sprite.rotation = self.rot

        #  debug updating
        if self._debug:
            self._debug_direction.vertices = [self.x, self.y, self.x + (cos((self.rot - 90) * pi / 180) * 100),
                                              self.y + (sin((self.rot - 90) * pi / 180) * -100)]
            self._debug_velocity.vertices = [self.x, self.y, self.x + self.vel_x * 0.5, self.y + self.vel_y * 0.5]

    def __contact__(self, rect):
        """check if self contacts rect, and slide if so"""
        line = self.hitbox.contacts(rect)

        if line is not None:
            self.__slide__(line, rect.friction)

    def __slide__(self, line, friction):
        """if velocity direction is towards line, set velocity parallel to line"""
        angle = line.angle()

        # get angle of self velocity
        vel_angle = atan2(self.vel_y, self.vel_x)

        # if velocity is towards line
        if angle - pi < vel_angle < angle:
            # get self total velocity
            vel = sqrt(self.vel_x ** 2 + self.vel_y ** 2)

            # get component of velocity that is parallel to line
            new_vel = cos(angle - vel_angle) * vel * friction

            # set self x, y velocity to this velocity & angle
            self.vel_x = new_vel * cos(angle)
            self.vel_y = new_vel * sin(angle)

    def debug_enable(self, batch, group = None):
        """enable drawing of rotation and velocity vectors"""
        self._debug = True

        self._debug_direction = batch.add(2, pgl.gl.GL_LINES, group, ('v2f/stream', (
            self.x, self.y, self.x + (cos((self.rot - 90) * pi / 180) * 100),
            self.y + (sin((self.rot - 90) * pi / 180) * -100))), ('c3B/static', (0, 255, 0, 0, 100, 0)))

        self._debug_velocity = batch.add(2, pgl.gl.GL_LINES, group, ('v2f/stream', (
            self.x, self.y, self.x + self.vel_x * 0.5, self.y + self.vel_y * 0.5)),
                                         ('c3B/static', (255, 0, 0, 100, 0, 0)))

    def debug_disable(self):
        """remove debug visuals from batch"""
        self._debug = False

        self._debug_direction.delete()
        self._debug_velocity.delete()

    def accelerate(self, x, y, mode = "absolute"):
        if mode == "absolute":
            """accelerate absolute motion of player"""
            self.vel_x += x
            self.vel_y += y

            self.__limit_velocity__(mode = 'absolute')
        elif mode == "relative":
            """accelerate motion of player relative to direction it is facing, cap at max_vel"""
            #  forward / backward acceleration
            self.vel_x += cos((self.rot + 90) * pi / 180) * -y
            self.vel_y += sin((self.rot + 90) * pi / 180) * y
            #  left / right acceleration
            self.vel_x += cos(self.rot * pi / 180) * x
            self.vel_y += sin(self.rot * pi / 180) * -x

            self.__limit_velocity__()
        else:
            raise ValueError("Invalid mode : {}".format(mode))

    def print_velocity(self):
        total_vel = sqrt(self.vel_x ** 2 + self.vel_y ** 2)
        return "{:.2f} (x: {:.2f}, y: {:.2f})".format(total_vel, self.vel_x, self.vel_y)

    def print_pos(self):
        return "x: {:.2f}, y: {:.2f}, rotation: {:.1f}".format(self.x, self.y, self.rot)

    def near_rect(self, rect):
        self._rects_in_range.append(rect)

    def set_pos(self, pos):
        self.x = pos[0]
        self.y = pos[1]

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
                    vel_ang = atan2(self.vel_y, self.vel_x)

                self.vel_x = cos(vel_ang) * self._max_vel
                self.vel_y = sin(vel_ang) * self._max_vel
