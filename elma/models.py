from abc import ABCMeta
import random
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
        picture_name (string): The name of the texture resource to use, without
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
        grass (boolean): A boolean deciding wether or the polygon is a grass
            polygon.
    """
    def __init__(self, points, grass=False):
        self.points = points
        self.grass = grass

    def __repr__(self):
        return 'Polygon(points: %s, grass: %s)' % (self.points, self.grass)

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


class Level(object):
    """
    Represent an Elastomania level.

    Attributes:
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
    """
    def __init__(self):
        self.polygons = []
        self.objects = []
        self.pictures = []
        self.level_id = random.randint(0, (2 ** 32) - 1)
        self.name = 'Unnamed'
        self.lgr = 'DEFAULT'
        self.ground_texture = 'ground'
        self.sky_texture = 'sky'

    def __repr__(self):
        return (('Level(level_id: %s, name: %s, lgr: %s, ' +
                 'ground_texture: %s, sky_texture: %s)') %
                (self.level_id, self.name, self.lgr,
                 self.ground_texture, self.sky_texture))


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
        time (float): The time at which the event occurs, given in 625/273ths
            of a second.
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


class GroundTouchAEvent(Event):
    """
    Represent a single replay ground touch A event.
    """
    def __init__(self):
        self.value = 0

    def __repr__(self):
        return 'GroundTouchAEvent(time: %s)' % self.time


class GroundTouchBEvent(Event):
    """
    Represent a single replay ground touch B event.
    """
    def __init__(self):
        self.value = 0

    def __repr__(self):
        return 'GroundTouchBEvent(time: %s)' % self.time


class Replay(object):
    """
    Represent an Elastomania replay.

    Attributes:
        is_multi (boolean): Whether or not the replay is a multiplayer replay.
        is_flagtag (boolean): Whether or not the replay is a flagtag replay.
        level_id (int): The unique identifier of the level this replay is from.
        level_name (string): The name of the level this replay is from.
        frames (list): The frames of this replay.
        events (list): The events of this replay.
    """
    def __init__(self):
        self.is_multi = False
        self.is_flagtag = False
        self.level_id = 0
        self.level_name = ''
        self.frames = []
        self.events = []
        # Needed to preserve unknown bits from rec files
        self._gas_and_turn_state = 0

    def get_exact_duration_in_seconds(self):
        """
        Calculates the exact replay duration in seconds.
        """
        return self.events[-1].time * 625/273

    def __repr__(self):
        return (
            'Replay(is_multi: %s, is_flagtag: %s, level_id: %s, ' +
            'level_name: %s, len(frames): %s, len(events): %s)') % (
            self.is_multi, self.is_flagtag, self.level_id, self.level_name,
            len(self.frames), len(self.events))
