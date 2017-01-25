from elma.constants import END_OF_DATA_MARKER
from elma.constants import END_OF_FILE_MARKER
from elma.constants import END_OF_REPLAY_FILE_MARKER
from elma.constants import TOP10_MULTIPLAYER
from elma.constants import TOP10_SINGLEPLAYER
from elma.models import Frame
from elma.models import GroundTouchAEvent
from elma.models import GroundTouchBEvent
from elma.models import LeftVoltEvent
from elma.models import Level
from elma.models import Obj
from elma.models import ObjectTouchEvent
from elma.models import Picture
from elma.models import Point
from elma.models import Polygon
from elma.models import Replay
from elma.models import RightVoltEvent
from elma.models import TurnEvent
from elma.utils import null_padded
import random
import struct

try:
    bytes('A', 'latin1')
    PY_VERSION = 3
except TypeError:
    PY_VERSION = 2
    bytes = lambda a, b: a
    _chr = chr
    chr = lambda a: a if type(a) == str else _chr(a)

packers = {
    'Point': lambda point:
        struct.pack('d', point.x) + struct.pack('d', point.y),
    'Polygon': lambda polygon: b''.join([
        struct.pack('I', polygon.grass),
        struct.pack('I', len(polygon.points)),
    ] + [pack_level(point) for point in polygon.points]),
    'Obj': lambda obj: b''.join([
        pack_level(obj.point),
        struct.pack('I', obj.type),
        struct.pack('I', obj.gravity),
        struct.pack('I', obj.animation_number)]),
    'Picture': lambda picture: b''.join([
        null_padded(picture.picture_name, 10),
        null_padded(picture.texture_name, 10),
        null_padded(picture.mask_name, 10),
        pack_level(picture.point),
        struct.pack('I', picture.distance),
        struct.pack('I', picture.clipping)])
}


def pack_level(item):
    """
    Pack a level-related item to its binary representation readable by
    Elastomania.
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

    return b''.join([
        bytes('POT14', 'latin1'),
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
    ] + [pack_level(polygon) for polygon in level.polygons] + [
        struct.pack('d', len(level.objects) + 0.4643643),
    ] + [pack_level(obj) for obj in level.objects] + [
        struct.pack('d', len(level.pictures) + 0.2345672),
    ] + [pack_level(picture) for picture in level.pictures] + [
        struct.pack('I', END_OF_DATA_MARKER),
    ] + [bytes(chr(c), 'latin1') for c in TOP10_SINGLEPLAYER] + [
    ] + [bytes(chr(c), 'latin1') for c in TOP10_MULTIPLAYER] + [
        struct.pack('I', END_OF_FILE_MARKER),
    ])


def unpack_level(data):
    """
    Unpack a level-related item from its binary representation readable by
    Elastomania.
    """

    data = iter(data)

    def munch(n):
        return b''.join([bytes(chr(next(data)), 'latin1') for _ in range(n)])

    level = Level()
    assert munch(5) == b'POT14'
    munch(2)
    level.level_id = struct.unpack('I', munch(4))[0]
    munch(8 * 4)
    level.name = munch(51).rstrip(b'\0').decode('latin1')
    level.lgr = munch(16).rstrip(b'\0').decode('latin1')
    level.ground_texture = munch(10).rstrip(b'\0').decode('latin1')
    level.sky_texture = munch(10).rstrip(b'\0').decode('latin1')

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
        object_type = struct.unpack('I', munch(4))[0]
        gravity = struct.unpack('I', munch(4))[0]
        animation_number = struct.unpack('I', munch(4))[0]
        level.objects.append(Obj(Point(x, y),
                                 object_type,
                                 gravity=gravity,
                                 animation_number=animation_number))

    number_of_pictures = int(struct.unpack('d', munch(8))[0])
    for _ in range(number_of_pictures):
        picture_name = munch(10).rstrip(b'\0').decode('latin1')
        texture_name = munch(10).rstrip(b'\0').decode('latin1')
        mask_name = munch(10).rstrip(b'\0').decode('latin1')
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


def unpack_replay(data):
    """
    Unpack a replay-related item from its binary representation readable by
    Elastomania.
    """

    data = iter(data)

    def munch(n):
        return b''.join([bytes(chr(next(data)), 'latin1') for _ in range(n)])

    def read_int32():
        return struct.unpack('i', munch(4))[0]

    def read_uint32():
        return struct.unpack('I', munch(4))[0]

    def read_int16():
        return struct.unpack('h', munch(2))[0]

    def read_uint8():
        return struct.unpack('B', munch(1))[0]

    def read_float():
        return struct.unpack('f', munch(4))[0]

    def read_double():
        return struct.unpack('d', munch(8))[0]

    replay = Replay()

    number_of_replay_frames = read_int32()
    munch(4)
    replay.is_multi = bool(read_int32())
    replay.is_flagtag = bool(read_int32())
    replay.level_id = read_uint32()
    replay.level_name = munch(12).rstrip(b'\0')
    munch(4)

    frame_numbers = range(number_of_replay_frames)
    xs = [read_float() for _ in frame_numbers]
    ys = [read_float() for _ in frame_numbers]
    left_wheel_xs = [read_int16() for _ in frame_numbers]
    left_wheel_ys = [read_int16() for _ in frame_numbers]
    right_wheel_xs = [read_int16() for _ in frame_numbers]
    right_wheel_ys = [read_int16() for _ in frame_numbers]
    head_xs = [read_int16() for _ in frame_numbers]
    head_ys = [read_int16() for _ in frame_numbers]
    rotations = [read_int16() for _ in frame_numbers]
    left_wheel_rotations = [read_uint8() for _ in frame_numbers]
    right_wheel_rotations = [read_uint8() for _ in frame_numbers]
    gas_and_turn_states = [read_uint8() for _ in frame_numbers]
    sound_effect_volumes = [read_int16() for _ in frame_numbers]

    for (x,
         y,
         left_wheel_x,
         left_wheel_y,
         right_wheel_x,
         right_wheel_y,
         head_x,
         head_y,
         rotation,
         left_wheel_rotation,
         right_wheel_rotation,
         gas_and_turn_state,
         sound_effect_volume) in zip(xs,
                                     ys,
                                     left_wheel_xs,
                                     left_wheel_ys,
                                     right_wheel_xs,
                                     right_wheel_ys,
                                     head_xs,
                                     head_ys,
                                     rotations,
                                     left_wheel_rotations,
                                     right_wheel_rotations,
                                     gas_and_turn_states,
                                     sound_effect_volumes):

        frame = Frame()
        frame.position = Point(x, y)
        frame.left_wheel_position = Point(left_wheel_x, left_wheel_y)
        frame.right_wheel_position = Point(right_wheel_x, right_wheel_y)
        frame.head_position = Point(head_x, head_y)
        frame.rotation = rotation
        frame.left_wheel_rotation = left_wheel_rotation
        frame.right_wheel_rotation = right_wheel_rotation
        frame.is_gasing = bool(gas_and_turn_state & 0b1)
        frame.is_turned_right = bool(gas_and_turn_state & 0b10)
        # preserve remaining 6 bits of state
        frame._gas_and_turn_state = gas_and_turn_state
        frame.spring_sound_effect_volume = sound_effect_volume
        replay.frames.append(frame)

    number_of_replay_events = read_int32()
    for _ in range(number_of_replay_events):
        event_time = read_double()
        event_type_1 = read_int32()
        event_type_2 = read_int32()

        if event_type_2 == 0:
            event = ObjectTouchEvent()
            event.object_number = event_type_1
        elif event_type_1 == 393215 and event_type_2 == 1065185444:
            event = TurnEvent()
        elif event_type_1 == 524287 and event_type_2 == 1065185444:
            event = LeftVoltEvent()
        elif event_type_1 == 458751 and event_type_2 == 1065185444:
            event = RightVoltEvent()
        elif event_type_1 == 131071:
            event = GroundTouchAEvent()
            event.value = event_type_2
        elif event_type_1 == 327679:
            event = GroundTouchBEvent()
            event.value = event_type_2

        event.time = event_time
        replay.events.append(event)

    return replay


def pack_replay(item):
    """
    Pack a replay-related item to its binary representation readable by
    Elastomania.
    """

    if isinstance(item, ObjectTouchEvent):
        return (struct.pack('d', item.time) +
                struct.pack('I', item.object_number) +
                struct.pack('I', 0))

    if isinstance(item, TurnEvent):
        return (struct.pack('d', item.time) +
                struct.pack('I', 393215) +
                struct.pack('I', 1065185444))

    if isinstance(item, LeftVoltEvent):
        return (struct.pack('d', item.time) +
                struct.pack('I', 524287) +
                struct.pack('I', 1065185444))

    if isinstance(item, RightVoltEvent):
        return (struct.pack('d', item.time) +
                struct.pack('I', 458751) +
                struct.pack('I', 1065185444))

    if isinstance(item, GroundTouchAEvent):
        return (struct.pack('d', item.time) +
                struct.pack('I', 131071) +
                struct.pack('I', item.value))

    if isinstance(item, GroundTouchBEvent):
        return (struct.pack('d', item.time) +
                struct.pack('I', 327679) +
                struct.pack('I', item.value))

    replay = item
    if PY_VERSION == 2:
        name = null_padded(replay.level_name, 12)
    else:
        name = null_padded(replay.level_name.decode('latin1'), 12)
    return b''.join([
        struct.pack('i', len(replay.frames)),
        struct.pack('i', 0x83),
        struct.pack('i', replay.is_multi),
        struct.pack('i', replay.is_flagtag),
        struct.pack('I', replay.level_id),
        name,
        struct.pack('i', 0),
        b''.join([struct.pack('f', frame.position.x)
                  for frame in replay.frames]),
        b''.join([struct.pack('f', frame.position.y)
                  for frame in replay.frames]),
        b''.join([struct.pack('h', frame.left_wheel_position.x)
                  for frame in replay.frames]),
        b''.join([struct.pack('h', frame.left_wheel_position.y)
                  for frame in replay.frames]),
        b''.join([struct.pack('h', frame.right_wheel_position.x)
                  for frame in replay.frames]),
        b''.join([struct.pack('h', frame.right_wheel_position.y)
                  for frame in replay.frames]),
        b''.join([struct.pack('h', frame.head_position.x)
                  for frame in replay.frames]),
        b''.join([struct.pack('h', frame.head_position.y)
                  for frame in replay.frames]),
        b''.join([struct.pack('h', frame.rotation)
                  for frame in replay.frames]),
        b''.join([struct.pack('B', frame.left_wheel_rotation)
                  for frame in replay.frames]),
        b''.join([struct.pack('B', frame.right_wheel_rotation)
                  for frame in replay.frames]),
        b''.join([struct.pack('B',
                              frame._gas_and_turn_state & 0b11111100 |
                              (frame.is_turned_right << 1) | frame.is_gasing)
                 for frame in replay.frames]),
        b''.join([struct.pack('h', frame.spring_sound_effect_volume)
                  for frame in replay.frames]),
        struct.pack('I', len(replay.events)),
        b''.join([pack_replay(event) for event in replay.events]),
        struct.pack('I', END_OF_REPLAY_FILE_MARKER),
    ])
