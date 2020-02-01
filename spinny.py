from pyglet.window import key
from game.player import Player
from game.tile import *
from game.debug import Debug

framerate = 60.0

game_window = pgl.window.Window(1280, 720)
key_handler = key.KeyStateHandler()
game_window.push_handlers(key_handler)

pgl.resource.path = ['resources']
pgl.resource.reindex()

main_batch = pgl.graphics.Batch()

tile_group = pgl.graphics.OrderedGroup(1)
player_group = pgl.graphics.OrderedGroup(2)
debug_group = pgl.graphics.OrderedGroup(3)
text_group = pgl.graphics.OrderedGroup(0)

pgl.gl.glLineWidth(2)


@game_window.event
def on_key_press(symbol, modifiers):
    if symbol == key.F3:
        debug.toggle_all()


@game_window.event
def on_draw():
    game_window.clear()
    main_batch.draw()


player1 = Player((150, 50), [[-5, -15], [-5, 15], [5, 15], [5, -15]], main_batch, player_group)
game_window.push_handlers(player1.key_handler)

objects = [player1]
tiles = [TilePipe((i * 51 + 50, 300), 0, main_batch, tile_group) for i in range(8)]

for tile in tiles:
    player1.near_rect(tile.hitbox)

debug = Debug(batch = main_batch, group = debug_group)

debug.add_group(tiles, 'tiles')
debug.add_group([player1, player1.hitbox], 'player')
debug.add_group(player1.smoke_particles, 'particles')

debug.dynamic_variable("Particles", player1.smoke_particles.get_particle_count, (10, 700), size = 15, anchor_x = 'left')
debug.dynamic_variable("Player velocity", player1.print_velocity, (10, 680), size = 15, anchor_x = 'left')
debug.dynamic_variable("Player position", player1.print_pos, (10, 660), size = 15, anchor_x = 'left')


def screen_wrap(obj):
    dist = 5

    if obj.x < 0 - dist:
        obj.x = game_window.width
    if obj.x > game_window.width + dist:
        obj.x = 0
    if obj.y < 0 - dist:
        obj.y = game_window.height
    if obj.y > game_window.height + dist:
        obj.y = 0


def update(dt):
    debug.update()

    player1.accelerate(0, -20)

    for obj in objects:
        obj.update(dt)
        screen_wrap(obj)


if __name__ == '__main__':
    pgl.clock.schedule_interval(update, 1 / framerate)
    pgl.app.run()
