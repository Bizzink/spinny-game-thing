import os.path
import pyglet as pgl
from .player import Player
from .debug import Debug
from .tile import TilePipe, TileAll, TileEnd


class Level:
    def __init__(self, current_version, supported_levels, window, batch):
        self._current_version = current_version
        self._supported_levels = supported_levels

        self.version = None
        self.player = None
        self._gravity = 20
        self._name = None
        self._start_pos = None
        self._data = {"tiles": [],
                      "particles": [],
                      "titles": []}

        self._window = window
        self._batch = batch

        self._player_group = pgl.graphics.OrderedGroup(0)
        self._background = pgl.graphics.OrderedGroup(1)
        self._foreground = pgl.graphics.OrderedGroup(2)
        self._debug_group = pgl.graphics.OrderedGroup(3)

        self.debug = Debug(self._batch, self._debug_group)

        """===================================================TEMPORARY==================================================="""
        self._data["tiles"] = [TilePipe((i * 51 + 50, 300), 0, self._batch, self._background) for i in range(8)]

    def update(self, dt):
        self.__screen_wrap__(self.player)
        self.player.accelerate(0, -self._gravity)
        self.player.update(dt)
        self.debug.update()

    def load(self, filename):
        filename += ".dat"

        if not os.path.isfile('levels/{}'.format(filename)):
            raise FileNotFoundError("File {} not found!".format(filename))

        else:
            with open("levels/{}".format(filename), "rb") as file:
                data = list(file.read())
                file.close()

            if data[0] not in self._supported_levels:
                raise ValueError(
                    "Level is unsupported version! ({}, supported: {})".format(data[0], self._supported_levels))

            self.player = Player((data[1], data[2]), self._batch, self._player_group)
            self._window.push_handlers(self.player.key_handler)

            """===================================================TEMPORARY==================================================="""
            for tile in self._data["tiles"]:
                self.player.near_rect(tile.hitbox)

            for val in data[3:]:
                pass
            # TODO: finish this

            self.debug.add_group(self._data["tiles"], 'tiles')
            self.debug.add_group([self.player, self.player.hitbox], 'player')
            self.debug.add_group(self.player.smoke_particles, 'particles')

            self.debug.dynamic_variable("Particles", self.player.smoke_particles.get_particle_count, (10, 700), size=15,
                                        anchor_x='left')
            self.debug.dynamic_variable("Player velocity", self.player.print_velocity, (10, 680), size=15, anchor_x='left')
            self.debug.dynamic_variable("Player position", self.player.print_pos, (10, 660), size=15, anchor_x='left')

    def save(self, filename):
        filename += ".dat"

        if os.path.isfile('levels/{}'.format(filename)):
            raise FileExistsError("File {} not already exists!".format(filename))

        else:
            data = [self._current_version, self._start_pos[0], self._start_pos[1]]

            for tile in self._data["tiles"]:
                data.append(tile.id)
                data.append([1, tile.x])
                data.append([2, tile.y])

                if tile.rot != 0:
                    data.append([3, tile.rot])

            for particle in self._data["particles"]:
                data.append(4)
                data.append([1, particle.x])
                data.append([2, particle.y])

                # TODO: finish this

            file = open("levels/{}".format(filename), "wb")
            file.write(bytes(data))
            file.close()

    def start_pos(self, pos):
        self._start_pos = pos

    def __screen_wrap__(self, obj):
        dist = 5

        if obj.x < 0 - dist:
            obj.x = self._window.width
        if obj.x > self._window.width + dist:
            obj.x = 0
        if obj.y < 0 - dist:
            obj.y = self._window.height
        if obj.y > self._window.height + dist:
            obj.y = 0
