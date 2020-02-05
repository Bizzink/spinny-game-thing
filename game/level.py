import os.path
import pyglet as pgl
from .player import Player
from .debug import Debug
from .tile import Tile
from .particle import PointEmitter


def to_bin(num):
    """convert a number to a list of 2 8 bit binary numbers"""
    if num > 65535:
        raise ValueError("Number out of range! ({} > 65536)".format(num))

    else:
        return [num // 255, num % 255]


def from_bin(byte_a, byte_b):
    """convert 2 bytes into a single number"""
    return (255 * byte_a) + byte_b


class Level:
    def __init__(self, current_version, supported_levels, window, batch):
        self._current_version = current_version
        self._supported_levels = supported_levels

        self.version = None
        self._name = None
        self._loaded = False
        self._data = {"tiles": [],
                      "particles": [],
                      "titles": [],
                      "start_pos": None,
                      "gravity": 20}

        self._window = window
        self._batch = batch

        self._background = pgl.graphics.OrderedGroup(0)
        self._player_group = pgl.graphics.OrderedGroup(1)
        self._foreground = pgl.graphics.OrderedGroup(2)
        self._debug_group = pgl.graphics.OrderedGroup(3)

        self.player = None

        self.debug = Debug(self._batch, self._debug_group)

    def update(self, dt):
        if self.player is not None:
            self.__screen_wrap__(self.player)
            self.player.accelerate(0, -self._data["gravity"])
            self.player.update(dt)
        self.debug.update()

        for particle in self._data["particles"]:
            particle.update(dt)

    def load(self, filename):
        """load data from file, refer to level_format.txt for details"""
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

            self.player = Player((from_bin(data[1], data[2]), from_bin(data[3], data[4])), batch=self._batch,
                                 group=self._player_group)
            self._window.push_handlers(self.player.key_handler)
            self._data["particles"].append(self.player.smoke_particles)

            self._data["gravity"] = data[5]

            index = 6

            while index < len(data):
                object_type = data[index]

                object_data = [object_type]

                # Tile
                if object_type == 1:
                    object_data.extend(data[index + 1: index + 10])
                    index += 10
                    param_id = data[index]

                    while param_id != 0:
                        object_data.append(param_id)
                        object_data.extend(data[index + 1: index + 4])
                        index += 4

                # PointEmitter
                elif object_type == 2:
                    object_data.extend(data[index + 1: index + 8])
                    index += 8
                    param_id = data[index]

                    while param_id != 0:
                        object_data.append(param_id)
                        index += 1

                        if param_id in (3, 5, 10, 15):  # 1 byte length
                            object_data.append(data[index])
                            index += 1

                        elif param_id in (1, 2, 4, 6, 7, 8, 9, 11, 12, 13):  # 2 byte length
                            object_data.extend(data[index: index + 2])
                            index += 2

                        else:  # 3 byte length
                            object_data.extend(data[index: index + 3])
                            index += 3

                # Create object
                self.__create_element__(object_data)
                index += 1

            self.__debug_setup__()
            self._loaded = True

    def load_empty(self):
        if not self._loaded:
            self._data = {"tiles": [],
                          "particles": [],
                          "titles": [],
                          "start_pos": None,
                          "gravity": 20}

        self._loaded = True

    def save(self, filename):
        """save items in data to a file, formatted as specified in level_format.txt"""
        filename += ".dat"

        if os.path.isfile('levels/{}'.format(filename)):
            raise FileExistsError("File {} already exists!".format(filename))

        else:
            if self._data["start_pos"] is None:
                self._data["start_pos"] = [0, 200, 1, 44]

            if self.player is not None:
                self._data["particles"].remove(self.player.smoke_particles)

            # Initial data
            data = [self._current_version]
            data.extend(self._data["start_pos"])
            data.append(self._data["gravity"])

            # Tiles data
            for tile in self._data["tiles"]:
                data.append(1)
                data.extend(to_bin(tile.x))
                data.extend(to_bin(tile.y))
                data.extend(to_bin(tile.rot))
                data.append(tile.shape)
                data.append(tile.style)

                if tile.has_outline:
                    data.append(1)
                else:
                    data.append(0)

                # Optional parameters
                if tile.colour != (255, 255, 255):
                    data.append(1)
                    data.extend(tile.colour)

                if tile.has_outline and tile.line_colour != (255, 255, 255):
                    data.append(2)
                    data.extend(tile.line_colour)

                data.append(0)

            # Particles data
            for particle in self._data["particles"]:
                emitter_data = [2]
                emitter_data.extend(to_bin(particle.x))
                emitter_data.extend(to_bin(particle.y))

                if particle.direction != 0:
                    data.append(1)
                    data.extend(to_bin(particle.direction))

                if particle.max_particles != 10:
                    data.append(2)
                    data.extend(to_bin(particle.max_particles))

                if particle.emit_speed != 1:
                    data.append(3)
                    data.append(particle.emit_speed)

                if particle.spread != 360:
                    data.append(4)
                    data.extend(to_bin(particle.spread))

                if particle.particle_image_id != 1:
                    data.append(5)
                    data.append(particle.particle_image_id)

                if particle.particle_vel != 10:
                    data.append(6)
                    data.extend(to_bin(particle.particle_vel))

                if particle.particle_vel_rand != 0:
                    data.append(7)
                    data.extend(to_bin(particle.particle_vel_rand))

                if particle.particle_rot_vel != 0:
                    data.append(8)
                    data.extend(to_bin(particle.particle_rot_vel))

                if particle.particle_rot_vel_rand != 0:
                    data.append(9)
                    data.extend(to_bin(particle.particle_rot_vel_rand))

                if particle.particle_size != 10:
                    data.append(10)
                    data.append(particle.particle_size)

                if particle.particle_size_rand != 0:
                    data.append(11)
                    data.extend(to_bin(particle.particle_size_rand))

                if particle.particle_lifetime != 1:
                    data.append(12)
                    data.extend(to_bin(particle.particle_lifetime))

                if particle.particle_lifetime_rand != 0:
                    data.append(13)
                    data.extend(to_bin(particle.particle_lifetime_rand))

                if particle.particle_colour != (255, 255, 255):
                    data.append(14)
                    data.extend(particle.particle_colour)

                if particle.particle_drag != 1:
                    data.append(15)
                    data.append(particle.particle_drag)

                data.append(0)

            file = open("levels/{}".format(filename), "wb")
            file.write(bytes(data))
            file.close()

    def unload(self):
        if self._loaded:
            self.player.delete()

            for tile in self._data["tiles"]:
                tile.delete()

            for particle in self._data["particles"]:
                particle.delete()

            for title in self._data["titles"]:
                title.delete()

            self.player = None
            self.version = None
            self._name = None
            self._data = {"tiles": [],
                          "particles": [],
                          "titles": [],
                          "start_pos": None,
                          "gravity": 20}

            self._loaded = False

    def __create_element__(self, data):
        """create a new object from the parameters in data, refer to level_format.txt for details"""
        #  Tile
        if data[0] == 1:
            pos_x = from_bin(data[1], data[2])
            pos_y = from_bin(data[3], data[4])
            rot = from_bin(data[5], data[6])
            shape_id = data[7]
            style_id = data[8]
            has_outline = bool(data[9])

            tile = Tile((pos_x, pos_y), rot, style_id, shape_id, outline = has_outline, batch = self._batch, group = self._background)

            index = 11

            while index < len(data):
                if data[index] == 1:  # tile colour
                    tile.set_colour(data[index + 1: index + 4])

                elif data[index] == 2:  # line colour
                    tile.set_outline_colour(data[index + 1, index + 4])

                index += 4

            self._data["tiles"].append(tile)

        #  Particle emitter
        elif data[0] == 4:
            data = data[1:]
            emitter = PointEmitter((0, 0), batch=self._batch, group=self._foreground)

            for i in range(len(data) // 3):
                var = data[i * 3]  # variable id
                val = from_bin(data[(i * 3) + 1], data[(i * 3) + 2])  # variable value

                if var == 1:
                    emitter.set_pos(val, emitter.y)
                elif var == 2:
                    emitter.set_pos(emitter.x, val)
                elif var == 3:
                    emitter.set_pos(emitter.x, emitter.y, direction=val)
                elif var == 4:
                    emitter.set_intensity(spread=val)
                elif var == 5:
                    emitter.set_intensity(max_particles=val)
                elif var == 6:
                    emitter.set_intensity(emit_speed=val)
                elif var == 7:
                    emitter.set_intensity(lifetime=val)
                elif var == 8:
                    emitter.set_intensity(lifetime_rand=val)
                elif var == 9:
                    emitter.set_intensity(size=val)
                elif var == 10:
                    emitter.set_intensity(size_rand=val)
                elif var == 11:
                    emitter.set_intensity(vel=val)
                elif var == 12:
                    emitter.set_intensity(vel_rand=val)
                elif var == 13:
                    emitter.set_intensity(rot_vel=val)
                elif var == 14:
                    emitter.set_intensity(rot_vel_rand=val)
                elif var == 15:
                    emitter.set_intensity(drag=val)

            self._data["particles"].append(emitter)

    def start_pos(self, pos):
        """set point at which player spawns"""
        self._data["start_pos"] = pos

    def __screen_wrap__(self, obj):
        """if object goes off one side of the screen, move it to the other side"""
        dist = 5

        if obj.x < 0 - dist:
            obj.x = self._window.width
        if obj.x > self._window.width + dist:
            obj.x = 0
        if obj.y < 0 - dist:
            obj.y = self._window.height
        if obj.y > self._window.height + dist:
            obj.y = 0

    def __debug_setup__(self):
        """add objects in self._data to debug groups"""
        self.debug.add_group(self._data["tiles"], 'tiles')
        self.debug.add_group([self.player, self.player.hitbox], 'player')
        self.debug.add_group(self._data["particles"], 'particles')

        particle_counts = [particle.get_particle_count for particle in self._data["particles"]]

        self.debug.dynamic_variable("Particles", particle_counts, (10, self._window.height - 20), size=15,
                                    anchor_x='left')
        self.debug.dynamic_variable("Player velocity", self.player.print_velocity, (10, self._window.height - 40),
                                    size=15, anchor_x='left')
        self.debug.dynamic_variable("Player position", self.player.print_pos, (10, self._window.height - 60), size=15,
                                    anchor_x='left')

        """===================================================TEMPORARY==================================================="""
        for tile in self._data["tiles"]:
            self.player.near_rect(tile.hitbox)

    def get_data(self):
        return self._data

    def is_loaded(self):
        return self._loaded
