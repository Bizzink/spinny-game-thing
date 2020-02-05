from time import sleep

from pyglet.window import key
import pyglet as pgl
from game.level import Level
from game import ui

from game.tile import Tile

framerate = 60.0
game_window = pgl.window.Window(1920, 1080)
pgl.resource.path = ['resources']
pgl.resource.reindex()
pgl.font.add_directory('resources/fonts')
main_batch = pgl.graphics.Batch()
cursor_hand = game_window.get_system_mouse_cursor(game_window.CURSOR_HAND)
cursor_normal = game_window.get_system_mouse_cursor(game_window.CURSOR_DEFAULT)


def get_version():
    """read version.txt to see what level versions are supported"""
    with open("version.txt") as file:
        data = file.read()
        curr, supp = None, None

        for line in data.split("\n"):
            name, val = line.split("=")
            name = name.strip()

            if name == "current_version":
                curr = int(val)
            elif name == "supported_versions":
                supp = []

                for item in val.split():
                    supp.append(int(val))

        return curr, supp


@game_window.event
def on_key_press(symbol, modifiers):
    if level.is_loaded():
        if symbol == key.F3:
            level.debug.toggle_all()

        if symbol == key.F2:
            level.save("test4")


@game_window.event
def on_mouse_press(x, y, button, modifiers):
    if button == pgl.window.mouse.LEFT:
        if not level.is_loaded():
            load_test.click(x, y)

        elif level.is_loaded():
            tile = Tile((x, y), 0, 1, 1, batch = main_batch, group = pgl.graphics.OrderedGroup(1))
            level._data["tiles"].append(tile)




@game_window.event
def on_mouse_motion(x, y, dx, dy):
    if not level.is_loaded():
        if load_test.hover(x, y):
            game_window.set_mouse_cursor(cursor_hand)

        else:
            pass
            game_window.set_mouse_cursor(cursor_normal)
    else:
        game_window.set_mouse_cursor(cursor_normal)


@game_window.event
def on_draw():
    game_window.clear()
    main_batch.draw()


def update(dt):
    if level.is_loaded():
        level.update(dt)


if __name__ == '__main__':
    # TODO: get all levels in folder and display scrolling list of them, function to call this menu whenever
    current, supported = get_version()
    level = Level(current, supported, game_window, main_batch)

    load_test = ui.Button((50, game_window.height // 2), "LOAD", "button_bg.png", level.load, params = "test4", batch = main_batch, group = pgl.graphics.OrderedGroup(1), anchor_x = 'left')
    #load_test = ui.Button((50, game_window.height // 2), "LOAD", "button_bg.png", level.load_empty, batch = main_batch, group = pgl.graphics.OrderedGroup(1), anchor_x = 'left')

    pgl.clock.schedule_interval(update, 1 / framerate)
    pgl.app.run()
