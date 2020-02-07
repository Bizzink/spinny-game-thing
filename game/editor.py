import pyglet as pgl
from .level import Level
from .ui import Button
from .tile import Tile
from .particle import PointEmitter


class Editor:
    def __init__(self, current_version, supported_levels, window, batch, level=None):
        if level is None:
            self._level = Level(current_version, supported_levels, window, batch)

        self._data = self._level.get_data()
        self._batch = batch
        self._window = window

        self._cursor_hand = self._window.get_system_mouse_cursor(self._window.CURSOR_HAND)
        self._cursor_normal = self._window.get_system_mouse_cursor(self._window.CURSOR_DEFAULT)

        self._background = pgl.graphics.OrderedGroup(0)
        self._player_group = pgl.graphics.OrderedGroup(1)
        self._foreground = pgl.graphics.OrderedGroup(2)

        self._button_group = pgl.graphics.OrderedGroup(4)

        self._show_options_button = Button((self._window.width - 50, self._window.height - 50), "",
                                           "options_button.png", 1,
                                           self.toggle_edit_buttons, kill_on_execute=False, batch=self._batch,
                                           group=self._button_group)

        self._buttons = [self._show_options_button]
        self._buttons_hover = False

        self._current_editor = None

        self._edit_buttons = None
        self._place = False

        self._current_object = {"type": None,
                                "params": {}}

    def mouse_press(self, x, y, button):
        """send mouse press event to buttons"""
        if button == pgl.window.mouse.LEFT:
            if self._buttons_hover:
                for button in self._buttons:
                    button.click(x, y)

            elif self._place:
                self.__place_object__(x, y)

    def mouse_hover(self, x, y):
        """check if the cursor his hovering over any buttons, and set it to hand if it is"""
        if any(button.hover(x, y) for button in self._buttons):
            self._window.set_mouse_cursor(self._cursor_hand)
            self._buttons_hover = True
        else:
            self._window.set_mouse_cursor(self._cursor_normal)
            self._buttons_hover = False

    def save(self, name):
        """save data to level"""
        self._level.set_data(self._data, mode="merge")
        self._level.save(name)

    def toggle_edit_buttons(self):
        if self._edit_buttons is None:
            self._current_editor = TileOptions(self._window.width, self._window.height - 30, self._batch, self._button_group)

    def __current_object_type__(self, obj_type):
        if obj_type in ("Tile", "PointEmitter"):
            self._current_object["type"] = obj_type

            if obj_type == "Tile":
                self._current_object["params"] = {"style_id": None, "shape_id": None, "outline": None,
                                                  "colour": None, "outline_colour": None}

        else:
            raise ValueError("Invalid object type: {}".format(obj_type))

    def __place_object__(self, x, y):
        if self._current_object["type"] == "Tile":
            style = self._current_object["params"]["style_id"]
            shape = self._current_object["params"]["shape_id"]

            tile = Tile((x, y), 0, style, shape, batch=self._batch, group=self._background)

            if self._current_object["params"]["colour"] is not None:
                tile.set_colour(self._current_object["params"]["colour"])

            if self._current_object["params"]["outline"] is True:
                tile.enable_outline()

            if self._current_object["params"]["outline_colour"] is not None:
                tile.set_outline_colour(self._current_object["params"]["outline_colour"])

            self._data["tiles"].append(tile)

        elif self._current_object["type"] == "PointEmitter":
            particle = PointEmitter(x, y)

            self.__particle_editor__(particle)

            self._data["particles"].append(particle)

    def __particle_editor__(self, particle):
        pass


class TileOptions:
    def __init__(self, x, y, batch, group):
        self._heading = pgl.text.Label("TILE", font_name="Ubuntu", font_size=30, x=x - 20, y = y,
                                       anchor_x="right", anchor_y="top", batch=batch, group=group)
        self._style_heading = pgl.text.Label("STYLE", font_name="Ubuntu", font_size=30, x=x - 20, y=y - 20,
                                             anchor_x="right", anchor_y="top", batch=batch, group=group)
        self._shape_heading = pgl.text.Label("SHAPE", font_name="Ubuntu", font_size=30, x=x - 20, y=y - 40,
                                             anchor_x="right", anchor_y="top", batch=batch, group=group)
