from elma.models import Point, Polygon
import unittest
from math import pi


class TestPolygon(unittest.TestCase):

    def test_move_by(self):
        poly1 = Polygon([Point(1, 2), Point(1, 3), Point(2, 2)])
        poly2 = Polygon([Point(0, 0), Point(0, 1), Point(1, 0)])
        poly2.move_by(1, 2)
        for p1, p2 in zip(poly1.points, poly2.points):
            self.assertEqual(p1, p2)

    def test_mirror(self):
        poly1 = Polygon([Point(1, 2), Point(1, 3), Point(2, 2)])
        poly2 = Polygon([Point(2, 2), Point(2, 3), Point(1, 2)])
        poly2.mirror()
        for p1, p2 in zip(poly1.points, poly2.points):
            self.assertEqual(p1, p2)

    def test_flip(self):
        poly1 = Polygon([Point(1, 2), Point(1, 3), Point(2, 2)])
        poly2 = Polygon([Point(1, 3), Point(1, 2), Point(2, 3)])
        poly2.flip()
        for p1, p2 in zip(poly1.points, poly2.points):
            self.assertEqual(p1, p2)

    def test_rotate(self):
        poly1 = Polygon([Point(1, 1), Point(0, 1), Point(1, 2)])
        poly2 = Polygon([Point(0, 0), Point(0, 1), Point(1, 0)])
        poly2.rotate(pi/2.0, Point(0, 1))
        for p1, p2 in zip(poly1.points, poly2.points):
            self.assertAlmostEqual(p1.x, p2.x)
            self.assertAlmostEqual(p1.y, p2.y)

    def test_scale(self):
        poly1 = Polygon([Point(1, 2), Point(1, 7), Point(3.5, 2)])
        poly2 = Polygon([Point(1, 2), Point(1, 4), Point(2, 2)])
        poly2.scale(2.5)
        for p1, p2 in zip(poly1.points, poly2.points):
            self.assertAlmostEqual(p1.x, p2.x)
            self.assertAlmostEqual(p1.y, p2.y)

    def test_center(self):
        poly = Polygon([Point(0, 0), Point(0, 2), Point(2, 2), Point(2, 0)])
        center = poly.center_point()
        self.assertAlmostEqual(center.x, 1.0)
        self.assertAlmostEqual(center.y, 1.0)
