import pyglet as pgl
from game.player import Player
from game.title import Title

framerate = 60.0

game_window = pgl.window.Window(1280, 720)

pgl.resource.path = ['resources']
pgl.resource.reindex()

main_batch = pgl.graphics.Batch()

player1 = Player((150, 50), main_batch)
game_window.push_handlers(player1.key_handler)

test = Title("test title", main_batch)

objects = [player1]

pgl.gl.glLineWidth(1)
debug = False


def update(dt):
    player1.acc_absolute(0, -20)
    for obj in objects:
        obj.update(dt)


@game_window.event
def on_draw():
    game_window.clear()

    if debug:
        player1.debug_draw()

    main_batch.draw()


if __name__ == '__main__':
    pgl.clock.schedule_interval(update, 1 / framerate)
    pgl.app.run()
