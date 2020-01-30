import pyglet as pgl
from math import cos, sin, pi


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return "Point ({}, {})".format(self.x, self.y)

    def __eq__(self, other):
        if isinstance(other, Point):
            if other.x == self.x and other.y == self.y:
                return True

        return False

    def set_pos(self, x, y):
        self.x = x
        self.y = y


class Rect:
    def __init__(self, pos, points):
        self.x = pos[0]
        self.y = pos[1]
        self.rot = 0

        self._points = [Point(point[0] + self.x, point[1] + self.y) for point in points]
        self._points_ref = [Point(point[0], point[1]) for point in points]

        self._checkbox = None
        self.checkbox_sides = {}
        self.__update_checkbox__()

        self._debug = False
        self._debug_vertex_list = []

    def update(self, x, y, rot):
        """update position and rotation"""
        self.__update_position__(x, y, rot)
        self.__update_checkbox__()

        if self._debug:
            for i in range(len(self._points)):
                self._debug_vertex_list[i].vertices = [self._points[i - 1].x, self._points[i - 1].y,
                                                       self._points[i].x, self._points[i].y]

            for i in range(len(self._checkbox)):
                j = i + len(self._points)
                self._debug_vertex_list[j].vertices = [self._checkbox[i - 1].x, self._checkbox[i - 1].y,
                                                       self._checkbox[i].x, self._checkbox[i].y]

    def contacts(self, rect):
        """check if self contacts other rect"""
        #  check if rects are in range
        if self.__in_range__(rect):
            #  check each side of rect to see if it intersects
            points = rect.get_points()

            for i in range(len(points)):
                line = [points[i - 1], points[i]]

                if self.__intersects__(line):
                    return line

            return None
        else:
            return None

    def debug_enable(self, batch, group = None):
        """enable drawing of rotation and velocity vectors"""
        self._debug = True
        self._debug_vertex_list = []

        for i in range(len(self._points)):
            vertex = batch.add(2, pgl.gl.GL_LINES, group, ('v2f', (self._points[i - 1].x,
                                                                   self._points[i - 1].y,
                                                                   self._points[i].x,
                                                                   self._points[i].y)),
                               ('c3B', (50, 50, 255, 50, 50, 255)))
            self._debug_vertex_list.append(vertex)

        for i in range(len(self._checkbox)):
            vertex = batch.add(2, pgl.gl.GL_LINES, group, ('v2f', ([self._checkbox[i - 1].x,
                                                                    self._checkbox[i - 1].y,
                                                                    self._checkbox[i].x,
                                                                    self._checkbox[i].y])),
                               ('c3B', (50, 255, 255, 50, 255, 255)))
            self._debug_vertex_list.append(vertex)

    def debug_disable(self):
        """remove debug visuals from batch"""
        self._debug = False

        for vertex in self._debug_vertex_list:
            vertex.delete()

        self._debug_vertex_list = None

    def debug_toggle(self, batch, group):
        """toggle debug on or off"""
        if self._debug:
            self.debug_disable()
        else:
            self.debug_enable(batch, group)

    def colour(self, colour, side=-1):
        """change colour of checkbox (for debug)"""
        if self._debug:
            colour.extend(colour)

            if side == -1:
                for i in range(len(self._points)):
                    self._debug_vertex_list[i].colors = colour
            else:
                self._debug_vertex_list[side].colors = colour

    def get_points(self):
        return self._points.copy()

    def __update_position__(self, x, y, rot):
        """move and rotate to specified position"""
        # rotate hitbox points around origin
        # method from https://stackoverflow.com/questions/2259476/rotating-a-point-about-another-point-2d
        self.x = x
        self.y = y
        self.rot = rot

        points = self._points_ref.copy()

        #  for some reason, self.rot needs to be negative, not sure why
        c, s = cos(-self.rot * pi / 180), sin(-self.rot * pi / 180)

        self._points = [Point(c * point.x - s * point.y + self.x, s * point.x + c * point.y + self.y) for point in
                        points]

    def __update_checkbox__(self):
        """update checkbox (bounding box of hitbox)"""
        #  Update box
        rect_x = [point.x for point in self._points]
        rect_y = [point.y for point in self._points]

        min_x = min(rect_x)
        max_x = max(rect_x)
        min_y = min(rect_y)
        max_y = max(rect_y)

        self._checkbox = [Point(min_x, min_y), Point(min_x, max_y), Point(max_x, max_y), Point(max_x, min_y)]

        self.checkbox_sides["min_x"] = min_x
        self.checkbox_sides["max_x"] = max_x
        self.checkbox_sides["min_y"] = min_y
        self.checkbox_sides["max_y"] = max_y

    def __in_range__(self, rect):
        """check if other rect is in range of self (checkboxes intersect)"""
        if self.checkbox_sides["min_x"] > rect.checkbox_sides["max_x"] or \
                self.checkbox_sides["max_x"] < rect.checkbox_sides["min_x"] or \
                self.checkbox_sides["min_y"] > rect.checkbox_sides["max_y"] or \
                self.checkbox_sides["max_y"] < rect.checkbox_sides["min_y"]:
            return False
        else:
            return True

    def __intersects__(self, line):
        """check if 2 line segments intersect.
        algorithm from https://bryceboe.com/2006/10/23/line-segment-intersection-algorithm/"""
        #  checks if 3 points are in an counterclockwise (ccw) configuration
        def ccw(point1, point2, point3):
            return (point3.y - point1.y) * (point2.x - point1.x) > (point2.y - point1.y) * (point3.x - point1.x)

        point_a = line[0]
        point_b = line[1]

        #  check to see if any line in self intersects with line
        for i in range(len(self._points)):
            point_c = self._points[i - 1]
            point_d = self._points[i]

            if ccw(point_a, point_c, point_d) != ccw(point_b, point_c, point_d) and \
                    ccw(point_a, point_b, point_c) != ccw(point_a, point_b, point_d):
                return True
