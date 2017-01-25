from elma.models import Level
from elma.models import Obj
from elma.models import Picture
from elma.models import Point
from elma.models import Polygon
from elma.packing import pack_level
from elma.packing import unpack_level
import unittest


class TestLevelPacking(unittest.TestCase):

    def test_packing(self):
        level = Level()
        # Specify level id to make testing easier
        level.level_id = 2535781587
        level.polygons = [Polygon([Point(0, 0), Point(0, 1), Point(1, 0)])]
        level.pictures = [Picture(Point(0, 0))]
        level.objects = [
            Obj(Point(0, 0), Obj.FLOWER),
            Obj(Point(0, 0), Obj.START),
            Obj(Point(0, 0), Obj.KILLER),
            Obj(Point(0, 0), Obj.FOOD),
            Obj(Point(0, 0), Obj.FOOD, gravity=Obj.GRAVITY_UP),
            Obj(Point(0, 0), Obj.FOOD, gravity=Obj.GRAVITY_DOWN),
            Obj(Point(0, 0), Obj.FOOD, gravity=Obj.GRAVITY_LEFT),
            Obj(Point(0, 0), Obj.FOOD, gravity=Obj.GRAVITY_RIGHT),
            Obj(Point(0, 0), Obj.FOOD, gravity=Obj.GRAVITY_NORMAL)
        ]
        packed = pack_level(level)
        original_level = level
        level = unpack_level(packed)
        self.assertEqual(2535781587, level.level_id)
        self.assertEqual('Unnamed', level.name)
        self.assertEqual('DEFAULT', level.lgr)
        self.assertEqual('ground', level.ground_texture)
        self.assertEqual('sky', level.sky_texture)

        # polygons
        self.assertEqual(1, len(level.polygons))
        self.assertEqual(Point(0, 0), level.polygons[0].points[0])
        self.assertEqual(Point(0, 1), level.polygons[0].points[1])
        self.assertEqual(Point(1, 0), level.polygons[0].points[2])

        # pictures
        self.assertEqual(1, len(level.pictures))
        picture = level.pictures[0]
        original_picture = original_level.pictures[0]
        self.assertEqual(original_picture.picture_name, picture.picture_name)
        self.assertEqual(original_picture.texture_name, picture.texture_name)
        self.assertEqual(original_picture.mask_name, picture.mask_name)
        self.assertEqual(original_picture.distance, picture.distance)
        self.assertEqual(original_picture.clipping, picture.clipping)

        # objects
        self.assertEqual(9, len(level.objects))
        for expected_obj, obj in zip([
                Obj(Point(0, 0), Obj.FLOWER),
                Obj(Point(0, 0), Obj.START),
                Obj(Point(0, 0), Obj.KILLER),
                Obj(Point(0, 0), Obj.FOOD),
                Obj(Point(0, 0), Obj.FOOD, gravity=Obj.GRAVITY_UP),
                Obj(Point(0, 0), Obj.FOOD, gravity=Obj.GRAVITY_DOWN),
                Obj(Point(0, 0), Obj.FOOD, gravity=Obj.GRAVITY_LEFT),
                Obj(Point(0, 0), Obj.FOOD, gravity=Obj.GRAVITY_RIGHT),
                Obj(Point(0, 0), Obj.FOOD, gravity=Obj.GRAVITY_NORMAL)
                ], level.objects):
            self.assertEqual(expected_obj, obj)
