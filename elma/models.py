import random


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


class Level(object):
    """
    Represents an Elastomania level.

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
