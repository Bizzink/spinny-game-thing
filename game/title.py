import pyglet as pgl


class Title:
    def __init__(self, text, pos, size = 30, colour = (255, 255, 255, 255), batch = None):
        self._label = pgl.text.Label(text = text, x = pos[0], y = pos[1], font_size = size, anchor_x = 'center', anchor_y = 'center', batch = batch, color = colour)

    def update_text(self, text):
        self._label.text = text

    def update_pos(self, pos):
        self._label.x = pos[0]
        self._label.y = pos[1]

    def update_size(self, size):
        self._label.font_size = size

    def update_colour(self, r, g, b, a = 255):
        self._label.color = (r, g, b, a)

    def update_font(self, font_name):
        self._label.font_name = font_name
