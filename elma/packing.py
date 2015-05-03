from constants import END_OF_DATA_MARKER
from constants import END_OF_FILE_MARKER
from constants import TOP10_MULTIPLAYER
from constants import TOP10_SINGLEPLAYER
from models import Level
from models import Obj
from models import Picture
from models import Point
from models import Polygon
from utils import null_padded
import random
import struct


packers = {
    'Point': lambda point:
        struct.pack('d', point.x) + struct.pack('d', point.y),
    'Polygon': lambda polygon: ''.join([
        struct.pack('I', polygon.grass),
        struct.pack('I', len(polygon.points)),
    ] + [pack(point) for point in polygon.points]),
    'Obj': lambda obj: ''.join([
        pack(obj.point),
        struct.pack('I', obj.type),
        struct.pack('I', obj.gravity),
        struct.pack('I', obj.animation_number)]),
    'Picture': lambda picture: ''.join([
        null_padded(picture.picture_name, 10),
        null_padded(picture.texture_name, 10),
        null_padded(picture.mask_name, 10),
        pack(picture.point),
        struct.pack('I', picture.distance),
        struct.pack('I', picture.clipping)])
}


def pack(item):
    """
    Pack an item to its binary representation readable by Elastomania.
    """
    if type(item).__name__ in packers:
        return packers[type(item).__name__](item)

    level = item
    polygon_checksum = sum([sum([point.x + point.y
                                 for point in polygon.points])
                            for polygon in level.polygons])
    object_checksum = sum([obj.point.x + obj.point.y + obj.type
                           for obj in level.objects])
    picture_checksum = sum([picture.point.x + picture.point.y
                            for picture in level.pictures])
    collected_checksum = 3247.764325643 * (polygon_checksum +
                                           object_checksum +
                                           picture_checksum)
    integrity_1 = collected_checksum
    integrity_2 = random.randint(0, 5871) + 11877 - collected_checksum
    integrity_3 = random.randint(0, 5871) + 11877 - collected_checksum
    integrity_4 = random.randint(0, 6102) + 12112 - collected_checksum
    assert ((integrity_3 - integrity_2) <= 5871)

    return ''.join([
        'POT14',
        struct.pack('H', level.level_id & 0xFFFF),
        struct.pack('I', level.level_id),
        struct.pack('d', integrity_1),
        struct.pack('d', integrity_2),
        struct.pack('d', integrity_3),
        struct.pack('d', integrity_4),
        null_padded(level.name, 51),
        null_padded(level.lgr, 16),
        null_padded(level.ground_texture, 10),
        null_padded(level.sky_texture, 10),
        struct.pack('d', len(level.polygons) + 0.4643643),
    ] + map(pack, level.polygons) + [
        struct.pack('d', len(level.objects) + 0.4643643),
    ] + map(pack, level.objects) + [
        struct.pack('d', len(level.pictures) + 0.2345672),
    ] + map(pack, level.pictures) + [
        struct.pack('I', END_OF_DATA_MARKER),
    ] + map(chr, TOP10_SINGLEPLAYER) + [
    ] + map(chr, TOP10_MULTIPLAYER) + [
        struct.pack('I', END_OF_FILE_MARKER),
    ])


def unpack(data):
    """
    Unpack an item from its binary representation readable by Elastomania.
    """

    data = iter(data)

    def munch(n):
        return ''.join([next(data) for _ in range(n)])

    level = Level()
    assert munch(5) == 'POT14'
    munch(2)
    level.level_id = struct.unpack('I', munch(4))[0]
    munch(8 * 4)
    level.name = munch(51).rstrip('\0')
    level.lgr = munch(16).rstrip('\0')
    level.ground_texture = munch(10).rstrip('\0')
    level.sky_texture = munch(10).rstrip('\0')

    number_of_polygons = int(struct.unpack('d', munch(8))[0])
    for _ in range(number_of_polygons):
        grass = struct.unpack('I', munch(4))[0]
        number_of_vertices = struct.unpack('I', munch(4))[0]
        points = []
        for __ in range(number_of_vertices):
            x = struct.unpack('d', munch(8))[0]
            y = struct.unpack('d', munch(8))[0]
            points.append(Point(x, y))
        level.polygons.append(Polygon(points, grass=grass))

    number_of_objects = int(struct.unpack('d', munch(8))[0])
    for _ in range(number_of_objects):
        x = struct.unpack('d', munch(8))[0]
        y = struct.unpack('d', munch(8))[0]
        type = struct.unpack('I', munch(4))[0]
        gravity = struct.unpack('I', munch(4))[0]
        animation_number = struct.unpack('I', munch(4))[0]
        level.objects.append(Obj(Point(x, y),
                                 type,
                                 gravity=gravity,
                                 animation_number=animation_number))

    number_of_pictures = int(struct.unpack('d', munch(8))[0])
    for _ in range(number_of_pictures):
        picture_name = munch(10)
        texture_name = munch(10)
        mask_name = munch(10)
        x = struct.unpack('d', munch(8))[0]
        y = struct.unpack('d', munch(8))[0]
        distance = struct.unpack('I', munch(4))[0]
        clipping = struct.unpack('I', munch(4))[0]
        level.pictures.append(Picture(Point(x, y),
                                      picture_name=picture_name,
                                      texture_name=texture_name,
                                      mask_name=mask_name,
                                      distance=distance,
                                      clipping=clipping))
    return level
