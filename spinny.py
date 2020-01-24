import pyglet as pgl
from game.player import Player
from game.title import Title

framerate = 60.0

game_window = pgl.window.Window()

pgl.resource.path = ['resources']
pgl.resource.reindex()

main_batch = pgl.graphics.Batch()

player1 = Player((150, 50), main_batch)
test = Title("test title", main_batch)

objects = [player1]


def update(dt):
    player1.acc_pos(1, 0)

    for obj in objects:
        obj.update(dt)


@game_window.event
def on_draw():
    game_window.clear()

    main_batch.draw()


if __name__ == '__main__':
    pgl.clock.schedule_interval(update, 1 / framerate)
    pgl.app.run()


