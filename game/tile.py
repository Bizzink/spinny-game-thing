import pyglet as pgl


class Tile:
    def __init__(self, pos, rot, image, hitbox, batch=None):
        self.x = pos[0]
        self.y = pos[1]
        self.rot = rot

        self.hitbox = hitbox
        self.area = self.__get__area__(self.hitbox)

        self._image = pgl.resource.image(image)
        self._image.center_x = self._image.width // 2
        self._image.center_y = self._image.height // 2
        self._image.anchor_x = self._image.width // 2
        self._image.anchor_y = self._image.height // 2
        self._sprite = pgl.sprite.Sprite(img=self._image, x=self.x, y=self.y, batch=batch)
        self._sprite.rotation = self.rot
        self._sprite.scale = 0.1

    def __get__area__(self):
        """get area of hitbox.
        algorithm from https://www.mathopenref.com/coordpolygonarea2.html"""
        x = [point[0] for point in self.hitbox]
        y = [point[1] for point in self.hitbox]
        points = len(self.hitbox)

        area = 0
        j = points - 1

        for i in range(points):
            area += (x[j] + x[i]) * (y[j] - y[i])
            j = i  # j is previous vertex to i

        return area / 2
