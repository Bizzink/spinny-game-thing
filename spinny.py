import pyglet as pgl
from game.player import Player
from game.title import Title
from math import cos, sin, pi

framerate = 60.0

game_window = pgl.window.Window()

pgl.resource.path = ['resources']
pgl.resource.reindex()

main_batch = pgl.graphics.Batch()

player1 = Player((150, 50), main_batch)
game_window.push_handlers(player1.key_handler)

test = Title("test title", main_batch)

objects = [player1]

pgl.gl.glLineWidth(1)
debug = True


def update(dt):
    player1.acc_absolute(0, -5)
    for obj in objects:
        obj.update(dt)


@game_window.event
def on_draw():
    game_window.clear()

    if debug:
        pgl.graphics.draw(2, pgl.gl.GL_LINES,
                          ('v2f', (player1.x, player1.y, player1.x + player1.vel_x, player1.y + player1.vel_y)),
                          ('c3B', (255, 0, 0, 100, 0, 0)))

        pgl.graphics.draw(2, pgl.gl.GL_LINES, ('v2f', (
            player1.x, player1.y, player1.x + (cos((player1.rot - 90) * pi / 180) * 100),
            player1.y + (sin((player1.rot - 90) * pi / 180) * -100))), ('c3B', (0, 255, 0, 0, 100, 0)))

    main_batch.draw()


if __name__ == '__main__':
    pgl.clock.schedule_interval(update, 1 / framerate)
    pgl.app.run()
