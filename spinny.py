from pyglet.window import key
import pyglet as pgl
from game.level import Level

game_window = pgl.window.Window(1280, 720)
framerate = 60.0

pgl.resource.path = ['resources']
pgl.resource.reindex()

main_batch = pgl.graphics.Batch()

pgl.gl.glLineWidth(2)


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
    if symbol == key.F3:
        level.debug.toggle_all()


@game_window.event
def on_draw():
    game_window.clear()
    main_batch.draw()


def update(dt):
    level.update(dt)


if __name__ == '__main__':
    current, supported = get_version()

    level = Level(current, supported, game_window, main_batch)
    level.load("test")

    pgl.clock.schedule_interval(update, 1 / framerate)
    pgl.app.run()
