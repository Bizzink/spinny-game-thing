from math import cos, sin, pi
from random import randrange
from time import time
import pyglet as pgl


class Particle:
    def __init__(self, pos, rot_vel, vel, drag, lifetime, image, size, batch=None, group=None):
        self._x = pos[0]
        self._y = pos[1]
        self.rot = 0
        self._rot_vel = rot_vel
        self._vel_x = vel[0]
        self._vel_y = vel[1]
        self._drag = drag

        self.age = time()
        self.lifetime = lifetime

        # sprite stuff
        self._image = pgl.resource.image(image)
        self._image.center_x = self._image.width // 2
        self._image.center_y = self._image.height // 2
        self._image.anchor_x = self._image.width // 2
        self._image.anchor_y = self._image.height // 2
        self._sprite = pgl.sprite.Sprite(img=self._image, x=self._x, y=self._y, batch=batch, group=group)
        self._sprite.scale = size / 10

        # debug stuff
        self.debug = False
        self._debug_vertex_list = None

    def __str__(self):
        return "Particle ({:.3f}, {:.3f}), vel = ({:.3f}, {:.3f}), rotation vel = {:.3f}, age = ({:.3f} / {})".format(self._x, self._y, self._vel_x, self._vel_y, self._rot_vel, time() - self.age, self.lifetime)

    def kill(self):
        """remove particle"""
        self._sprite.delete()

        if self._debug_vertex_list is not None:
            for vertex in self._debug_vertex_list:
                vertex.delete()

        del self

    def update(self, dt):
        self._x += self._vel_x * dt
        self._y += self._vel_y * dt
        self.rot += self._rot_vel * dt

        self.__drag__()

        self._sprite.x = self._x
        self._sprite.y = self._y
        self._sprite.rotation = self.rot

        if self.debug:
            self._debug_vertex_list[0].vertices = [self._x, self._y, self._x + (cos(self.rot * pi / 180) * 30),
                                                   self._y + (sin(self.rot * pi / 180) * -30)]
            self._debug_vertex_list[1].vertices = [self._x, self._y, self._x + self._vel_x * 0.1,
                                                   self._y + self._vel_y * 0.1]

    def __drag__(self):
        """gradually slow velocity"""
        self._vel_x *= self._drag
        self._vel_y *= self._drag

    def debug_enable(self, batch, group=None):
        """enable drawing of rotation and velocity vectors"""
        self.debug = True

        debug_direction = batch.add(2, pgl.gl.GL_LINES, group, ('v2f/stream', (
            self._x, self._y, self._x + (cos(self.rot * pi / 180) * 30),
            self._y + (sin(self.rot * pi / 180) * -30))), ('c3B/static', (0, 255, 0, 0, 100, 0)))

        debug_velocity = batch.add(2, pgl.gl.GL_LINES, group, ('v2f/stream', (
            self._x, self._y, self._x + self._vel_x * 0.1, self._y + self._vel_y * 0.1)),
                                   ('c3B/static', (255, 0, 0, 100, 0, 0)))

        self._debug_vertex_list = [debug_direction, debug_velocity]

    def debug_disable(self):
        """disable drawing ov debug vectors"""
        self.debug = False
        for vertex in self._debug_vertex_list:
            vertex.delete()

        self._debug_vertex_list = None


class PointEmitter:
    def __init__(self, pos, max_particles = 10, emit_speed = 1, direction = 0, rot_vel = 0, rot_vel_rand = 0, spread = 360, vel = 10, vel_rand = 0, image = "square.png", size = 10, size_rand = 0, drag = 1, lifetime = 1, lifetime_rand = 0, batch = None, group = None):
        """rotation related items are in degrees! - rot_vel, rot_vel_rand, direction, spread"""
        # emitter parameters
        self.x = pos[0]
        self.y = pos[1]
        self.max_particles = max_particles
        self.emit_speed = emit_speed
        self.direction = direction
        self.spread = spread
        self._batch = batch
        self._group = group

        # particle parameters
        self.particle_rot_vel = rot_vel
        self.particle_rot_vel_rand = rot_vel_rand
        self.particle_vel = vel
        self.particle_vel_rand = vel_rand
        self.particle_size = size
        self.particle_size_rand = size_rand
        self.particle_drag = drag
        self.particle_image = image
        self.particle_lifetime = lifetime
        self.particle_lifetime_rand = lifetime_rand

        # other
        self._debug = False
        self._debug_vertex_list = None
        self._debug_group = None
        self._time_since_emit = 0
        self._particles = []

    def update(self, dt):
        self._time_since_emit += dt

        if self._time_since_emit > 1 / self.emit_speed and len(self._particles) < self.max_particles:
            self._particles.append(self.__emit__())
            self._time_since_emit = 0

        for particle in self._particles:
            particle.update(dt)

            if time() - particle.age > particle.lifetime:
                particle.kill()
                self._particles.remove(particle)

        if self._debug:
            for particle in self._particles:
                if not particle.debug:
                    particle.debug_enable(self._batch, self._debug_group)

    def __emit__(self):
        """create new particle with randomised parameters within range of limits"""
        rot_vel = self.particle_rot_vel
        if self.particle_rot_vel_rand != 0: rot_vel += randrange(-self.particle_rot_vel_rand // 2, self.particle_rot_vel_rand // 2)

        vel = self.particle_vel
        if self.particle_vel_rand != 0: vel += randrange(-self.particle_vel_rand // 2, self.particle_vel_rand // 2)

        lifetime = self.particle_lifetime
        if self.particle_lifetime_rand != 0: lifetime += randrange(((-self.particle_lifetime_rand * 1000) // 2), ((self.particle_lifetime_rand * 1000) // 2)) / 1000

        direction = self.direction
        if self.spread != 0: direction += randrange(-self.spread // 2, self.spread // 2)
        direction = (cos(direction * pi / 180) * vel, -sin(direction * pi / 180) * vel)

        size = self.particle_size / 10
        if self.particle_size_rand != 0: size += randrange(-self.particle_size_rand // 2, self.particle_size_rand // 2) / 100

        particle = Particle((self.x, self.y), rot_vel, direction, self.particle_drag, lifetime, self.particle_image, size, self._batch, self._group)

        return particle

    def set_pos(self, x, y, direction = None):
        """set positon, rotation from which particles are emitted"""
        self.x = x
        self.y = y

        if direction is not None:
            self.direction = direction

        if self._debug:
            self._debug_vertex_list[0].vertices = [self.x, self.y,
                                                   self.x + (cos((self.direction - (self.spread // 2)) * pi / 180) * self.particle_vel * self.particle_lifetime),
                                                   self.y + (sin((self.direction - (self.spread // 2)) * pi / 180) * -self.particle_vel * self.particle_lifetime)]
            self._debug_vertex_list[1].vertices = [self.x, self.y,
                                                   self.x + (cos((self.direction + (self.spread // 2)) * pi / 180) * self.particle_vel * self.particle_lifetime),
                                                   self.y + (sin((self.direction + (self.spread // 2)) * pi / 180) * -self.particle_vel * self.particle_lifetime)]
            self._debug_vertex_list[2].vertices = [self.x, self.y,
                                                   self.x + (cos(self.direction * pi / 180) * self.particle_vel * self.particle_lifetime),
                                                   self.y + (sin(self.direction * pi / 180) * -self.particle_vel * self.particle_lifetime)]

    def set_intensity(self, vel = None, vel_rand = None, rot_vel = None, rot_vel_rand = None, emit_speed = None, size = None, size_rand = None, spread = None, max_particles = None, lifetime = None, lifetime_rand = None, drag = None):
        """change parameters related to intensity of particles emitted"""
        # emitter parameters
        if max_particles is not None: self.max_particles = max_particles
        if emit_speed is not None: self.emit_speed = emit_speed
        if spread is not None: self.spread = spread

        # particle parameters
        if vel is not None: self.particle_vel = vel
        if rot_vel is not None: self.particle_rot_vel = rot_vel
        if rot_vel_rand is not None: self.particle_rot_vel_rand = rot_vel_rand
        if vel_rand is not None: self.particle_vel_rand = vel_rand
        if size is not None: self.particle_size = size
        if size_rand is not None: self.particle_size_rand = size_rand
        if lifetime is not None: self.particle_lifetime = lifetime
        if lifetime_rand is not None: self.particle_lifetime_rand = lifetime_rand
        if drag is not None: self.particle_drag = drag

    def debug_enable(self, batch, group = None):
        """enable drawing of direction vector, spread cone of emitter"""
        self._debug = True
        self._debug_group = group

        for particle in self._particles:
            particle.debug_enable(batch, group)

        angle1 = batch.add(2, pgl.gl.GL_LINES, group, ('v2f/stream', (
            self.x, self.y, self.x + (cos((self.direction - (self.spread // 2)) * pi / 180) * self.particle_vel * self.particle_lifetime),
            self.y + (sin((self.direction - (self.spread // 2)) * pi / 180) * -self.particle_vel * self.particle_lifetime))), ('c3B/static', (50, 50, 255, 50, 50, 200)))

        angle2 = batch.add(2, pgl.gl.GL_LINES, group, ('v2f/stream', (
            self.x, self.y, self.x + (cos((self.direction + (self.spread // 2)) * pi / 180) * self.particle_vel * self.particle_lifetime),
            self.y + (sin((self.direction + (self.spread // 2)) * pi / 180) * -self.particle_vel * self.particle_lifetime))), ('c3B/static', (50, 50, 255, 50, 50, 200)))

        direction = batch.add(2, pgl.gl.GL_LINES, group, ('v2f/stream', (
            self.x, self.y, self.x + (cos(self.direction * pi / 180) * self.particle_vel * self.particle_lifetime),
            self.y + (sin(self.direction * pi / 180) * -self.particle_vel * self.particle_lifetime))), ('c3B/static', (255, 0, 0, 200, 0, 0)))

        self._debug_vertex_list = [angle1, angle2, direction]

    def debug_disable(self):
        """disable drawing of debug vectors"""
        self._debug = False

        for vertex in self._debug_vertex_list:
            vertex.delete()

        self._debug_vertex_list = None

        for particle in self._particles:
            particle.debug_disable()

    def get_particle_count(self):
        """return amount of particles current alive in system"""
        return len(self._particles)

    def delete(self):
        for particle in self._particles:
            particle.kill()
