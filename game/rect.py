import pyglet as pgl
from math import cos, sin, pi


class Rect:
    def __init__(self, pos, points):
        self.x = pos[0]
        self.y = pos[1]
        self.rot = 0

        self._points = [[point[0] + self.x, point[1] + self.y] for point in points]
        self._points_ref = points

        self._checkbox = None
        self.checkbox_sides = {}
        self._checkbox_area = 0
        self.__update_checkbox__()

        self._area = 0
        self.__get__area__()

        self._debug = False
        self._debug_vertex_list = []

    def update(self, x, y, rot):
        self.__update_position__(x, y, rot)
        self.__update_checkbox__()

        if self._debug:
            for i in range(len(self._points)):
                self._debug_vertex_list[i].vertices = [self._points[i - 1][0], self._points[i - 1][1],
                                                       self._points[i][0], self._points[i][1]]

            for i in range(len(self._checkbox)):
                j = i + len(self._points)
                self._debug_vertex_list[j].vertices = [self._checkbox[i - 1][0], self._checkbox[i - 1][1],
                                                       self._checkbox[i][0], self._checkbox[i][1]]

    def contacts(self, rect):
        return self.__in_range__(rect)

    def debug_enable(self, batch, group=None):
        """enable drawing of rotation and velocity vectors"""
        self._debug = True

        for i in range(len(self._points)):
            vertex = batch.add(2, pgl.gl.GL_LINES, group, ('v2f', (self._points[i - 1][0],
                                                                   self._points[i - 1][1],
                                                                   self._points[i][0],
                                                                   self._points[i][1])),
                               ('c3B', (50, 50, 255, 50, 50, 255)))
            self._debug_vertex_list.append(vertex)

        for i in range(len(self._checkbox)):
            vertex = batch.add(2, pgl.gl.GL_LINES, group, ('v2f', ([self._checkbox[i - 1][0],
                                                                    self._checkbox[i - 1][1],
                                                                    self._checkbox[i][0],
                                                                    self._checkbox[i][1]])),
                               ('c3B', (50, 255, 255, 50, 255, 255)))
            self._debug_vertex_list.append(vertex)

    def debug_disable(self):
        """remove debug visuals from batch"""
        self._debug = False

        for vertex in self._debug_vertex_list:
            vertex.delete()

    def debug_toggle(self, batch, group):
        """toggle debug on or off"""
        if self._debug:
            self.debug_disable()
        else:
            self.debug_enable(batch, group)

    def checkbox_colour(self, colour):
        colour.extend(colour)

        for i in range(len(self._checkbox)):
            j = i + len(self._points)
            self._debug_vertex_list[j].colors = colour

    def __update_position__(self, x, y, rot):
        """rotate hitbox points around origin
        method from https://stackoverflow.com/questions/2259476/rotating-a-point-about-another-point-2d"""
        self.x = x
        self.y = y
        self.rot = rot

        points = [point.copy() for point in self._points_ref.copy()]

        #  for some reason, self.rot needs to be negative, not sure why
        c, s = cos(-self.rot * pi / 180), sin(-self.rot * pi / 180)

        self._points = [[c * point[0] - s * point[1] + self.x, s * point[0] + c * point[1] + self.y] for point in
                        points]

    def __update_checkbox__(self):
        """update checkbox (bounding box of hitbox)"""
        #  Update box
        rect_x = [point[0] for point in self._points]
        rect_y = [point[1] for point in self._points]

        min_x = min(rect_x)
        max_x = max(rect_x)
        min_y = min(rect_y)
        max_y = max(rect_y)

        self._checkbox = [[min_x, min_y], [min_x, max_y], [max_x, max_y], [max_x, min_y]]

        self.checkbox_sides["min_x"] = min_x
        self.checkbox_sides["max_x"] = max_x
        self.checkbox_sides["min_y"] = min_y
        self.checkbox_sides["max_y"] = max_y

        #  get area
        self._checkbox_area = (max_x - min_x) * (max_y - min_y)

    def __get__area__(self):
        """get area of hitbox.
        algorithm from https://www.mathopenref.com/coordpolygonarea2.html"""
        #  rect area
        x, y = [], []

        for point in self._points:
            x.append(point[0])
            y.append(point[1])

        points = len(self._points)

        area = 0
        j = points - 1

        for i in range(points):
            area += (x[j] + x[i]) * (y[j] - y[i])
            j = i  # j is previous vertex to i

        self.area = area / 2

    def __in_range__(self, rect):
        """check if other rect is in range of self (checkboxes intersect)"""
        if self.checkbox_sides["min_x"] > rect.checkbox_sides["max_x"] or \
                self.checkbox_sides["max_x"] < rect.checkbox_sides["min_x"] or \
                self.checkbox_sides["min_y"] > rect.checkbox_sides["max_y"] or \
                self.checkbox_sides["max_y"] < rect.checkbox_sides["min_y"]:
            return False
        else:
            return True
