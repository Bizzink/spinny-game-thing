import pyglet as pgl


class Button:
    def __init__(self, pos, dim, title, action, params = None, batch = None, group = None, font_colour = (255, 255, 255, 255), background_image = None, anchor_x = "center", anchor_y = "center"):
        self._action = action
        self._params = params
        self._has_background = background_image is not None
        self._batch = batch
        
        # anchor types:
        #   x: left, center, right
        #   y: top, center, bottom
        # Note: y values are from bottom up

        if anchor_x == "left":
            self._min_x = pos[0]
            self._max_x = pos[0] + dim[0]
        elif anchor_x == "center":
            self._min_x = pos[0] - dim[0] // 2
            self._max_x = pos[0] + dim[0] // 2
        elif anchor_x == "right":
            self._min_x = pos[0] - dim[0]
            self._max_x = pos[0]
        else:
            raise ValueError("Invalid value for anchor_x: {}! (should be 'left', 'center' or 'right')".format(anchor_x))

        if anchor_y == "top":
            self._min_y = pos[1] - dim[1]
            self._max_y = pos[1]
        elif anchor_y == "center":
            self._min_y = pos[1] - dim[1] // 2
            self._max_y = pos[1] + dim[1] // 2
        elif anchor_y == "bottom":
            self._min_y = pos[1]
            self._max_y = pos[1] + dim[1]
        else:
            raise ValueError("Invalid value for anchor_y: {}! (should be 'top', 'center' or 'bottom')".format(anchor_x))

        self._center = (self._min_x + dim[0] // 2, self._min_y + dim[1] // 2)

        # Label setup

        text_group = None
        if group is not None:
            text_group = pgl.graphics.OrderedGroup(group.order + 1)

        self._label = pgl.text.Label(text = title.upper(), x = self._center[0], y = self._center[1], font_name = 'Ubuntu',
                                     color = font_colour, font_size = 50, batch = batch, group = text_group)

        #  background setup

        if background_image is not None:
            self._image = pgl.resource.image(pgl.image.load(background_image))
            
            self._image.center_x = self._center[0]
            self._image.center_y = self._center[1]
            self._image.anchor_x = self._image.width // 2
            self._image.anchor_y = self._image.height // 2
            
            self._background = pgl.sprite.Sprite(img = self._image, x = self._center[0], y = self._center[1],
                                                 batch = batch, group = group)

    def update_label(self, text = None, colour = None):
        if text is not None:
            self._label.text = text

        if colour is not None:
            self._label.color = colour
    
    def click(self, x, y):
        """run action if mouse is withing button boundaries"""
        if self.__check_click__(x, y):
            if self._params is not None:
                self._action(self._params)
                self.delete()
            else:
                self._action()
                self.delete()

    def __check_click__(self, x, y):
        """check if position is within boundaries of button"""
        if x < self._min_x:
            return False 
        if x > self._max_x:
            return False
        if y < self._min_y:
            return False
        if y > self._max_y:
            return False
        
        return True

    def delete(self):
        self._label.delete()

        if self._has_background:
            self._background.delete()

        del self
