import pyglet as pgl


class Button:
    def __init__(self, pos, title, image, size, action, kill_on_execute = False, params = None, batch = None, group = None, bg_colour = (150, 150, 150), font_colour = (255, 255, 255, 255), anchor_x = "center", anchor_y = "center"):
        self._action = action
        self._params = params
        self._kill_on_execute = kill_on_execute
        self._batch = batch

        #  background setup
        self._image = pgl.resource.image(image)
        self._image.x = pos[0]
        self._image.y = pos[1]

        if anchor_x == "left":
            self._image.anchor_x = 0
            self._text_x = pos[0] + (self._image.width // 2) * size / 5

        elif anchor_x == "center":
            self._image.anchor_x = self._image.width // 2
            self._text_x = pos[0]

        elif anchor_x == "right":
            self._image.anchor_x = self._image.width
            self._text_x = pos[0] - (self._image.width // 2) * size / 5
        else:
            raise ValueError("{} is invalid for anchor_x! (must be 'left', 'right' or 'center')".format(anchor_x))

        if anchor_y == "bottom":
            self._image.anchor_y = 0
            self._text_y = pos[0] + (self._image.height // 2) * size / 5

        elif anchor_y == "center":
            self._image.anchor_y = self._image.height // 2
            self._text_y = pos[1]

        elif anchor_y == "top":
            self._image.anchor_y = self._image.height
            self._text_y = pos[0] - (self._image.height // 2) * size / 5
        else:
            raise ValueError("{} is invalid for anchor_y! (must be 'bottom', 'top' or 'center')".format(anchor_y))

        self._background = pgl.sprite.Sprite(img = self._image, x = pos[0], y = pos[1],
                                             batch=batch, group=group)
        self._background.color = bg_colour
        self._background.scale = size / 5

        # Label setup
        text_group = None
        if group is not None:
            text_group = pgl.graphics.OrderedGroup(group.order + 1)

        self._label = pgl.text.Label(text = title.upper(), x = self._text_x, y = self._text_y + size * 5, font_name = 'Ubuntu',
                                     color = font_colour, font_size = size * 30, batch = batch, group = text_group,
                                     anchor_x = 'center', anchor_y = 'center')

    def update_label(self, text = None, colour = None):
        if text is not None:
            self._label.text = text

        if colour is not None:
            self._label.color = colour
    
    def click(self, x, y):
        """run action if mouse is withing button boundaries"""
        if self.hover(x, y):
            if self._params is not None:
                self._action(self._params)

            else:
                self._action()

            if self._kill_on_execute:
                self.delete()

    def hover(self, x, y):
        """check if position is within boundaries of button"""
        if not self._text_x - self._background.width // 2 < x < self._text_x + self._background.width // 2:
            return False

        if not self._text_y - self._background.height // 2 < y < self._text_y + self._background.height // 2:
            return False
        
        return True

    def delete(self):
        self._label.delete()
        self._background.delete()
        del self
