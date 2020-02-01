from pyglet.window import key
from game.player import Player
from game.tile import *
from game.debug import Debug

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

player1 = Player((150, 50), [[-5, -15], [-5, 15], [5, 15], [5, -15]], main_batch, player_group)
game_window.push_handlers(player1.key_handler)

objects = [player1]
tiles = [TilePipe((i * 51 + 50, 300), 0, main_batch, tile_group) for i in range(8)]

debug = Debug(batch = main_batch, group = debug_group)
debug.add_group(tiles, 'tiles')
debug.add_group([player1, player1.hitbox], 'player')
debug.add_group(player1.smoke_particles, 'particles')

debug.dynamic_variable("Particles", player1.smoke_particles.get_particle_count, (10, 700), size = 15, anchor_x = 'left')
debug.dynamic_variable("Player velocity", player1.print_velocity, (10, 680), size = 15, anchor_x = 'left')
debug.dynamic_variable("Player position", player1.print_pos, (10, 660), size = 15, anchor_x = 'left')

pgl.gl.glLineWidth(2)

test_line = None


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
    global debug, test_line
    if key_handler[key.F3]:
        if key.F3 not in prev_keys:
            prev_keys.append(key.F3)
            debug.toggle_all()

    if not key_handler[key.F3]:
        if key.F3 in prev_keys:
            prev_keys.remove(key.F3)

    debug.update()

    player1.accelerate(0, -20)

    contact_line = None
    contact_friction = 1

    if test_line is not None:
        test_line.delete()
        test_line = None

    for tile in tiles:
        line = player1.hitbox.contacts(tile.hitbox)

        if line is not None:
            contact_line = line
            contact_friction = tile.friction

            if debug:
                player1.hitbox.colour([50, 255, 50])
                tile.hitbox.colour([50, 255, 50])

        else:
            if debug:
                player1.hitbox.colour([50, 50, 255])
                tile.hitbox.colour([50, 50, 255])

    player1.slide_line = contact_line
    player1.slide_friction = contact_friction

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
