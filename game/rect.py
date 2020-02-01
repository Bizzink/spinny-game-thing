import pyglet as pgl
from math import cos, sin, pi, atan2


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


class Line:
    def __init__(self, points):
        self._points = points

        self._debug = False
        self._debug_vertex = None

    def update(self, points):
        self._points = points

        if self._debug:
            self._debug_vertex.vertices = [self._points[0].x, self._points[0].y, self._points[1].x, self._points[1].y]

    def get_points(self):
        return self._points.copy()

    def contacts(self, line):
        """check if 2 line segments intersect.
        algorithm from https://bryceboe.com/2006/10/23/line-segment-intersection-algorithm/"""

        #  checks if 3 points are in an counterclockwise (ccw) configuration
        def ccw(point1, point2, point3):
            return (point3.y - point1.y) * (point2.x - point1.x) > (point2.y - point1.y) * (point3.x - point1.x)

        point_a, point_b = line.get_points()
        point_c = self._points[0]
        point_d = self._points[1]

        if ccw(point_a, point_c, point_d) != ccw(point_b, point_c, point_d) and ccw(point_a, point_b, point_c) != ccw(
                point_a, point_b, point_d):
            return True
        return False

    def min_x(self):
        return min(self._points[0].x, self._points[1].x)

    def min_y(self):
        return min(self._points[0].y, self._points[1].y)

    def max_x(self):
        return max(self._points[0].x, self._points[1].x)

    def max_y(self):
        return max(self._points[0].y, self._points[1].y)

    def angle(self):
        """return angle of line"""
        dy = self._points[1].y - self._points[0].y
        dx = abs(self._points[0].x - self._points[1].x)
        angle = atan2(dy, dx) + pi

        if self._points[0].x > self._points[1].x:
            dy = self._points[0].y - self._points[1].y
            angle = atan2(dy, dx)

        if angle > pi * 2: angle -= pi * 2

        return angle

    def debug_enable(self, batch, group = None):
        """disable debug vertex rendering"""
        self._debug = True
        self._debug_vertex = batch.add(2, pgl.gl.GL_LINES, group, (
            'v2f', (self._points[0].x, self._points[0].y, self._points[1].x, self._points[1].y)),
                                       ('c3B', (255, 255, 50, 255, 255, 50)))

    def debug_disable(self):
        """disable debug vertex rendering"""
        self._debug = False
        self._debug_vertex.delete()
        self._debug_vertex = None

    def colour(self, colour):
        """set colour of debug vertex"""
        if self._debug:
            self._debug_vertex.colors = colour


class Rect:
    def __init__(self, pos, points):
        self.x = pos[0]
        self.y = pos[1]
        self.rot = 0

        self._points = [Point(point[0] + self.x, point[1] + self.y) for point in points]
        self._points_ref = [Point(point[0], point[1]) for point in points]
        self._sides = [Line([points[i - 1], points[i]]) for i in range(len(points))]

        self.friction = 0.9

        self._checkbox = None
        self.checkbox_sides = {}
        self.__update_checkbox__()

        self._debug = False
        self._debug_vertex_list = []

    def update(self, x, y, rot):
        """update position and rotation"""
        self.__update_position__(x, y, rot)
        self.__update_sides__()
        self.__update_checkbox__()

        if self._debug:
            for i in range(4):
                self._debug_vertex_list[i].vertices = [self._checkbox[i - 1].x, self._checkbox[i - 1].y,
                                                       self._checkbox[i].x, self._checkbox[i].y]

    def contacts(self, rect):
        """check if self contacts other rect"""
        #  check if rects are in range
        if self.__in_range__(rect):
            #  check each side of rect to see if it intersects
            rect_sides = rect.get_sides()

            for rect_side in rect_sides:
                for side in self._sides:
                    if side.contacts(rect_side):
                        return rect_side
        return None

    def debug_enable(self, batch, group=None):
        """enable drawing of rotation and velocity vectors"""
        self._debug = True

        for side in self._sides:
            side.debug_enable(batch, group)

        self._debug_vertex_list = []

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

        for side in self._sides:
            side.debug_disable()

        for vertex in self._debug_vertex_list:
            vertex.delete()

        self._debug_vertex_list = None

    def colour(self, colour, side=-1):
        """change colour of checkbox (for debug)"""
        if self._debug:
            colour.extend(colour)

            if side == -1:
                for side in self._sides:
                    side.colour(colour)
            else:
                self._sides[side].colour(colour)

    def get_points(self):
        return self._points.copy()

    def get_sides(self):
        return self._sides.copy()

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

    def __update_sides__(self):
        for i in range(len(self._sides)):
            self._sides[i].update([self._points[i - 1], self._points[i]])

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
