import pyglet as pgl
from game.player import Player
from game.title import Title
import resources


def center_image(image):
    """Sets an image's anchor point to its center"""
    image.anchor_x = image.width // 2
    image.anchor_y = image.height // 2


game_window = pgl.window.Window()

pgl.resource.path = ['resources']
pgl.resource.reindex()

player1 = Player((150, 50))
test = Title("test title")


@game_window.event
def on_draw():
    game_window.clear()

    test.draw()
    player1.draw()


if __name__ == '__main__':
    pgl.app.run()
