import pyglet as pgl


class Title:
    def __init__(self, text, batch = None):
        self._label = pgl.text.Label(text = text, x = 100, y = 100, anchor_x = 'center', anchor_y = 'center', batch = batch)

    def draw(self):
        self._label.draw()
