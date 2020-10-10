import itertools
from abc import ABCMeta
from typing import List, Optional
from PIL import Image
from elma.constants import VERSION_ELMA
from elma.render import LevelRenderer
from elma.utils import null_padded, BoundingBox
import random
import struct
from math import cos, sin


class Point(object):
    """
    Represent a single 2D point.

    Attributes:
        x (float): The x-coordinate of the point.
        y (float): The y-coordinate of the point.
    """
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return 'Point(x: %s, y: %s)' % (self.x, self.y)

    def __eq__(self, other_point):
        return self.x == other_point.x and self.y == other_point.y


class Obj(object):
    """
    Represent an Elastomania level object, which can be one of: flower, food,
    killer, start.

    Attributes:
        point (Point): The 2D Point that represents the position of the object.
            type (int): The type of the object, which should be one of:
            Obj.FLOWER, Obj.FOOD, Obj.Killer, Obj.START.
        gravity (int): The gravity of the object, if the object is a food
            object. It should be one of: Obj.GRAVITY_NORMAL, Obj.GRAVITY_UP,
            Obj.GRAVITY_DOWN, Obj.GRAVITY_LEFT, Obj,GRAVITY_RIGHT.
        animation_number (int): The animation number of the object.
    """

    FLOWER = 1
    FOOD = 2
    KILLER = 3
    START = 4

    GRAVITY_NORMAL = 0
    GRAVITY_UP = 1
    GRAVITY_DOWN = 2
    GRAVITY_LEFT = 3
    GRAVITY_RIGHT = 4

    def __init__(self, point, type,
                 gravity=GRAVITY_NORMAL, animation_number=1):
        self.point = point
        self.type = type
        self.gravity = gravity
        self.animation_number = animation_number

    def __repr__(self):
        return (
            'Obj(point: %s, type: %s, gravity: %s, animation_number: %s)' %
            (self.point, self.type, self.gravity, self.animation_number))

    def __eq__(self, other_obj):
        return (self.point == other_obj.point and
                self.type == other_obj.type and
                self.gravity == other_obj.gravity and
                self.animation_number == other_obj.animation_number)


class Picture(object):
    """
    Represents an Elastomania level picture.

    Attributes:
        point (Point): The 2D Point that represents the position of the object.
        picture_name (string): The name of the picture resource to use, without
            .PCX, e.g. 'BARREL'.
        texture_name (string): The name of the texture resource to use, without
            .PCX, e.g. 'STONE1'.
        mask_name (string): The name of the texture resource to use, without
            .PCX, e.g. 'MASKHOR'.
        distance (int): The z-ordering distance of the picture. Should be in
            the range 1-999.
        clipping (int): The clipping of the picture. Should be one of:
            Picture.CLIPPING_U, Picture.CLIPPING_G, Picture.CLIPPING_S.
    """

    CLIPPING_U = 0
    CLIPPING_G = 1
    CLIPPING_S = 2

    def __init__(self, point, picture_name='', texture_name='',
                 mask_name='', distance=500, clipping=CLIPPING_U):
        self.point = point
        self.picture_name = picture_name
        self.texture_name = texture_name
        self.mask_name = mask_name
        self.distance = distance
        self.clipping = clipping

    def __repr__(self):
        return (
            ('Picture(point: %s, picture_name: %s, texture_name: %s,' +
             'mask_name: %s, distance: %s, clipping: %s)') %
            (self.point, self.picture_name, self.texture_name,
             self.mask_name, self.distance, self.clipping))

    def __eq__(self, other_picture):
        return (self.point == other_picture.point and
                self.picture_name == other_picture.picture_name and
                self.texture_name == other_picture.texture_name and
                self.mask_name == other_picture.mask_name and
                self.distance == other_picture.distance and
                self.clipping == other_picture.clipping)


class Polygon(object):
    """
    Represents an Elastomania level polygon.

    Attributes:
        points (list): A list of Points defining the polygon contour.
        grass (boolean): A boolean deciding whether or not the polygon is a
            grass polygon.
    """
    def __init__(self, points, grass=False):
        self.points = points
        self.grass = grass

    def __repr__(self):
        return 'Polygon(points: %s, grass: %s)' % (self.points, self.grass)

    def __eq__(self, other_polygon):
        return (self.points == other_polygon.points and
                self.grass == other_polygon.grass)

    def move_by(self, x=0, y=0):
        self.points = [Point(p.x + x, p.y + y) for p in self.points]

    def mirror(self):
        mirror_axis = (self.rightmost_point().x +
                       self.leftmost_point().x) / 2.0
        for p in self.points:
            p.x = 2 * mirror_axis - p.x

    def flip(self):
        flip_axis = (self.highest_point().y + self.lowest_point().y) / 2.0
        for p in self.points:
            p.y = 2 * flip_axis - p.y

    def rotate(self, angle, fixed_point=None):
        if fixed_point is None:
            fixed_point = self.center_point()
        for p in self.points:
            norm_x = p.x - fixed_point.x
            norm_y = p.y - fixed_point.y
            p.x = norm_x * cos(angle) - norm_y * sin(angle) + fixed_point.x
            p.y = norm_x * sin(angle) + norm_y * cos(angle) + fixed_point.y

    def scale(self, scaler):
        fixed_point = Point(self.leftmost_point().x, self.lowest_point().y)
        for p in self.points:
            p.x = scaler * (p.x - fixed_point.x) + fixed_point.x
            p.y = scaler * (p.y - fixed_point.y) + fixed_point.y

    def center_point(self):
        center = Point(0.0, 0.0)
        for p in self.points:
            center.x += p.x
            center.y += p.y
        center.x /= len(self.points)
        center.y /= len(self.points)
        return center

    def rightmost_point(self):
        return max(self.points, key=lambda p: p.x)

    def leftmost_point(self):
        return min(self.points, key=lambda p: p.x)

    def highest_point(self):
        return max(self.points, key=lambda p: p.y)

    def lowest_point(self):
        return min(self.points, key=lambda p: p.y)

    def area(self) -> float:
        """
        Returns the area of the polygon
        """
        return abs(self._signed_area())

    def is_ordered_clockwise(self) -> bool:
        """
        Returns True if the points of the polygon are ordered clockwise and
        False if counterclockwise.
        """
        return self._signed_area() < 0

    def is_filled(self) -> bool:
        """
        Returns True if the interior of the polygon is filled.
        """
        return not self.is_ordered_clockwise()

    def _signed_area(self) -> float:
        """
        Returns the signed area of the polygon.
        """
        points = self.points
        area = (points[0].x - points[-1].x) * (points[0].y + points[-1].y)
        for i in range(len(self.points) - 1):
            area += (points[i + 1].x - points[i].x) * (points[i + 1].y + points[i].y)
        return area / 2


class Top10Time(object):
    """
    Represents a top10 time.

    Attributes:
        time (int): The finished time in hundredths.
        kuski (string): The name of the first player.
        kuski2 (string): The name of the second player. Should equal kuski for
            singleplayer times.
        is_multi (boolean): Whether or not the time is a multiplayer time.
    """
    def __init__(self, time, kuski, kuski2=None, is_multi=False):
        self.time = time
        self.kuski = kuski
        self.kuski2 = kuski if kuski2 is None else kuski2
        self.is_multi = is_multi

    def __repr__(self):
        if self.is_multi:
            return ('Top10Time(time: %s, kuski: %s, kuski2: %s)' %
                    (self.time, self.kuski, self.kuski2))
        else:
            return 'Top10Time(time: %s, kuski: %s)' % (self.time, self.kuski)

    def __eq__(self, other_time):
        return (self.time == other_time.time and
                self.kuski == other_time.kuski and
                self.kuski2 == other_time.kuski2)


class Top10(object):
    """
    Represents the complete top10 of a level with both singleplayer
    and multiplayer times, up to 10 times of each.

    Attributes:
        single (list): A list of up to 10 singleplayer Top10Times.
        multi (list): A list of up to 10 multiplayer Top10Times.
    """
    def __init__(self):
        self.single = []
        self.multi = []

    def __repr__(self):
        return 'Top10(single: %s, multi: %s)' % (self.single, self.multi)

    def sort(self):
        self.single = sorted(self.single, key=lambda t: t.time)[:10]
        self.multi = sorted(self.multi, key=lambda t: t.time)[:10]

    def merge(self, other_top10):
        for s in self.single:
            for o in other_top10.single:
                if s.time == o.time and s.kuski == o.kuski:
                    other_top10.single.remove(o)
                    break
        self.single.extend([o for o in other_top10.single])

        for s in self.multi:
            for o in other_top10.multi:
                if (s.time == o.time and s.kuski == o.kuski and
                      s.kuski2 == o.kuski2):
                    other_top10.multi.remove(o)
                    break
        self.multi.extend([o for o in other_top10.multi])
        self.sort()

    def to_buffer(self):
        self.sort()
        return b''.join([
            struct.pack('I', len(self.single)),
            b''.join([struct.pack('I', t.time) for t in self.single]),
            b''.join([struct.pack('I', 0)
                      for _ in range(10 - len(self.single))]),
            b''.join([null_padded(t.kuski, 15) for t in self.single]),
            b''.join([null_padded('', 15)
                      for _ in range(10 - len(self.single))]),
            b''.join([null_padded(t.kuski2, 15) for t in self.single]),
            b''.join([null_padded('', 15)
                      for _ in range(10 - len(self.single))]),
            struct.pack('I', len(self.multi)),
            b''.join([struct.pack('I', t.time) for t in self.multi]),
            b''.join([struct.pack('I', 0)
                      for _ in range(10 - len(self.multi))]),
            b''.join([null_padded(t.kuski, 15) for t in self.multi]),
            b''.join([null_padded('', 15)
                      for _ in range(10 - len(self.multi))]),
            b''.join([null_padded(t.kuski2, 15) for t in self.multi]),
            b''.join([null_padded('', 15)
                      for _ in range(10 - len(self.multi))]),
        ])


class Level(object):
    """
    Represent an Elastomania level.

    Attributes:
        version (string): VERSION_ELMA ('POT14') or VERSION_ACROSS ('POT06').
        polygons (list): A list of Polygons in the level.
        objects (list): A list of Objects in the level.
        pictures (list): A list of Pictures in the level.
        level_id (int): A unique unsigned 32bit integer level identifier.
        name (string): The name of level, which should be no longer than 50
            characters long.
        lgr (string): The name of the LGR used for this level, which should be
            no longer than 10 characters long.
        ground_texture (string): The name of the ground texture used for this
            level, which should be no longer than 10 characters long.
        sky_texture (string): The name of the sky texture used for this level,
            which should be no longer than 10 characters long.
        top10 (Top10): A Top10 for the level.
        preserve_integrity_values (boolean): Whether or not to unpack and
            preserve the existing integrity values, instead of recomputing
            them when packing.
        integrity (list): A list of four integrity values read from an existing
            level. Empty, if preserve_integrity_values is False.
    """
    def __init__(self):
        self.version = VERSION_ELMA
        self.polygons = []
        self.objects = []
        self.pictures = []
        self.level_id = random.randint(0, (2 ** 32) - 1)
        self.name = 'Unnamed'
        self.lgr = 'DEFAULT'
        self.ground_texture = 'ground'
        self.sky_texture = 'sky'
        self.top10 = Top10()
        self.preserve_integrity_values = False
        self.integrity = []

    @property
    def ground_polygons(self) -> List[Polygon]:
        """
        Returns all non-grass polygons of the level.
        """
        return [polygon for polygon in self.polygons if not polygon.grass]

    @property
    def grass_polygons(self) -> List[Polygon]:
        """
        Returns all grass polygons of the level.
        """
        return [polygon for polygon in self.polygons if polygon.grass]

    def as_image(self,
                 *,
                 max_width: Optional[int] = LevelRenderer.DEFAULT_WIDTH,
                 max_height: Optional[int] = LevelRenderer.DEFAULT_HEIGHT,
                 scale: Optional[float] = None,
                 padding: int = LevelRenderer.DEFAULT_PADDING,
                 render_objects: bool = True,
                 show: bool = False) -> Image:
        """
        Render image of the level.

        Args:
            max_width: max width of the image (ignored if scale is provided)
            max_height: max height of the image (ignored if scale is provided)
            scale: scaling factor to convert level coordinates to pixels,
                overrides max_width and max_height
            padding: space around the image in pixels
            render_objects: render both objects and polygons if True,
                else render only polygons
            show: show rendered image if True
        """
        if scale:
            renderer = LevelRenderer.with_scale(level=self, scale=scale, padding=padding)
        else:
            renderer = LevelRenderer(level=self, max_width=max_width, max_height=max_height, padding=padding)
        if show:
            renderer.show(render_objects=render_objects)
        return renderer.render(render_objects=render_objects)

    def min_x(self) -> float:
        """
        Returns the minimum x coordinate of all vertices, pictures and objects.
        """
        return min([p.x for p in self._all_points()])

    def max_x(self) -> float:
        """
        Returns the maximum x coordinate of all vertices, pictures and objects.
        """
        return max([p.x for p in self._all_points()])

    def min_y(self) -> float:
        """
        Returns the minimum y coordinate of all vertices, pictures and objects.
        """
        return min([p.y for p in self._all_points()])

    def max_y(self) -> float:
        """
        Returns the maximum y coordinate of all vertices, pictures and objects.
        """
        return max([p.y for p in self._all_points()])

    def bounding_box(self) -> BoundingBox:
        """
        Returns the bounding box of the level.
        """
        return BoundingBox(self.min_x(), self.max_x(), self.min_y(), self.max_y())

    def _all_points(self) -> List[Point]:
        """
        Returns all coordinate points of vertices, pictures and level objects.
        """
        vertex_points = list(itertools.chain(*[polygon.points for polygon in self.polygons]))
        picture_points = [pic.point for pic in self.pictures]
        object_points = [obj.point for obj in self.objects]
        return vertex_points + picture_points + object_points

    def __repr__(self):
        return (('Level(level_id: %s, name: %s, lgr: %s, ' +
                 'ground_texture: %s, sky_texture: %s)') %
                (self.level_id, self.name, self.lgr,
                 self.ground_texture, self.sky_texture))

    def __eq__(self, other_level):
        # level_id, integrity and name can differ
        return (self.polygons == other_level.polygons and
                self.objects == other_level.objects and
                self.pictures == other_level.pictures)


class Frame(object):
    """
    Represent a single replay frame.

    Attributes:
        position (Point): The position of the kuski in this frame in level
            coordinates.
        left_wheel_position (Point): The position of the bike's left wheel in
            this frame relative to the position of the kuski.
        right_wheel_position (Point): The position of the bike's right wheel in
            this frame relative to the position of the kuski.
        head_position (point): The position of the kuski's head in this frame
            relative to the position of the kuski.
        rotation (int): The rotation of the kuski in 10000ths of a radian.
        left_wheel_rotation (int): The rotation of the bike's left wheel in
            249/2/pi-ths of a radian.
        right_wheel_rotation (int): The rotation of the bike's right wheel in
            249/2/pi-ths of a radian.
        is_gasing (boolean): Whether or not the bike is gasing in this frame.
        is_turned_right (boolean): Whether or not the bike is turned right in
            this frame.
        spring_sound_effect_volume (int): The spring sound effect volume for
            this frame.
    """
    def __init__(self):
        self.position = Point(0, 0)
        self.left_wheel_position = Point(0, 0)
        self.right_wheel_position = Point(0, 0)
        self.head_position = Point(0, 0)
        self.rotation = 0
        self.left_wheel_rotation = 0
        self.right_wheel_rotation = 0
        self.is_gasing = 0
        self.is_turned_right = 0
        self.spring_sound_effect_volume = 0

    def __repr__(self):
        return ('Frame(position: %s, left_wheel_position: %s, ' +
                'right_wheel_position: %s, head_position: %s, ' +
                'rotation: %s, left_wheel_rotation: %s, ' +
                'right_wheel_rotation: %s, is_gasing: %s, ' +
                'is_turned_right: %s, spring_sound_effect_volume: %s)') % (
                    self.position,
                    self.left_wheel_position,
                    self.right_wheel_position,
                    self.head_position,
                    self.rotation,
                    self.left_wheel_rotation,
                    self.right_wheel_rotation,
                    self.is_gasing,
                    self.is_turned_right,
                    self.spring_sound_effect_volume)


class Event(object):
    """
    Abstract base representation of a single replay event.

    Attributes:
        time (float): The time at which the event occurs, given in
            0.001/(0.182*0.0024)ths of a second.
    """
    __metaclass__ = ABCMeta

    def __init__(self):
        self.time = 0

    def __repr__(self):
        return 'Event(time: %s)' % self.time


class ObjectTouchEvent(Event):
    """
    Represent a single replay object touch event.
    """
    def __init__(self):
        self.object_number = 0

    def __repr__(self):
        return 'ObjectTouchEvent(time: %s, object_number: %s)' % (
               self.time, self.object_number)


class TurnEvent(Event):
    """
    Represent a single replay turn event.
    """
    def __repr__(self):
        return 'TurnEvent(time: %s)' % self.time


class LeftVoltEvent(Event):
    """
    Represent a single replay left volt event.
    """
    def __repr__(self):
        return 'LeftVoltEvent(time: %s)' % self.time


class RightVoltEvent(Event):
    """
    Represent a single replay right volt event.
    """
    def __repr__(self):
        return 'RightVoltEvent(time: %s)' % self.time


class GroundTouchEvent(Event):
    """
    Represent a single replay ground touch event.
    """
    def __init__(self):
        self.value = 0

    def __repr__(self):
        return 'GroundTouchEvent(time: %s)' % self.time


class AppleTouchEvent(Event):
    """
    Represent an apple touch event. This is always generated together with the ObjectTouchEvent when touching an apple.
    """
    def __repr__(self):
        return 'AppleTouchEvent(time: %s)' % self.time


class Replay(object):
    """
    Represent an Elastomania replay.

    Attributes:
        is_finished (boolean): Whether or not the replay is (probably) finished.
        is_multi (boolean): Whether or not the replay is a multiplayer replay.
        is_flagtag (boolean): Whether or not the replay is a flagtag replay.
        level_id (int): The unique identifier of the level this replay is from.
        level_name (string): The name of the level this replay is from.
        frames (list): The frames of this replay.
        events (list): The events of this replay.
        time (float): The time of this replay in seconds.
    """
    def __init__(self):
        self.is_finished = False
        self.is_multi = False
        self.is_flagtag = False
        self.level_id = 0
        self.level_name = ''
        self.frames = []
        self.events = []
        self.time = 0.0
        # Needed to preserve unknown bits from rec files
        self._gas_and_turn_state = 0

    def __repr__(self):
        return (
            'Replay(is_multi: %s, is_flagtag: %s, level_id: %s, ' +
            'level_name: %s, len(frames): %s, len(events): %s)') % (
            self.is_multi, self.is_flagtag, self.level_id, self.level_name,
            len(self.frames), len(self.events))
