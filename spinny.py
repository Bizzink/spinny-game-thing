import pyglet as pgl
from pyglet.window import key
from game.player import Player
from game.title import Title
from game.tile import *
import math

framerate = 60.0

game_window = pgl.window.Window(1280, 720)
key_handler = key.KeyStateHandler()
game_window.push_handlers(key_handler)

prev_keys = []

pgl.resource.path = ['resources']
pgl.resource.reindex()

main_batch = pgl.graphics.Batch()

tile_group = pgl.graphics.OrderedGroup(1)
player_group = pgl.graphics.OrderedGroup(2)
debug_group = pgl.graphics.OrderedGroup(3)
text_group = pgl.graphics.OrderedGroup(0)

player1 = Player((150, 50), main_batch, player_group)
game_window.push_handlers(player1.key_handler)

title_test = Title("debug off", (100, 50), batch=main_batch, group=text_group)

block = TileAll((200, 300), 0, batch = main_batch, group = tile_group)
block2 = TilePipe((200, 250), 0, batch=main_batch,group=tile_group)
block3 = TileEnd((300, 250), 0, batch=main_batch,group=tile_group)

objects = [player1]
tiles = [block, block2, block3]
debug = False

pgl.gl.glLineWidth(1)


def screen_wrap(obj):
    dist = 300

    if obj.x < 0 - dist:
        obj.x = game_window.width
    if obj.x > game_window.width + dist:
        obj.x = 0
    if obj.y < 0 - dist:
        obj.y = game_window.height
    if obj.y > game_window.height + dist:
        obj.y = 0


def update(dt):
    global debug
    if key_handler[key.F3]:
        if key.F3 not in prev_keys:
            prev_keys.append(key.F3)
            debug = True
            for obj in objects:
                obj.debug_toggle(main_batch, debug_group)
            for tile in tiles:
                tile.debug_toggle(main_batch, debug_group)

            if debug:
                title_test.update_text("debug on")
            else:
                title_test.update_text("debug off")

    if not key_handler[key.F3]:
        if key.F3 in prev_keys:
            prev_keys.remove(key.F3)

    player1.acc_absolute(0, -20)
    for obj in objects:

        obj.update(dt)

    screen_wrap(player1)


@game_window.event
def on_draw():
    game_window.clear()

    main_batch.draw()


if __name__ == '__main__':
    pgl.clock.schedule_interval(update, 1 / framerate)
    pgl.app.run()
