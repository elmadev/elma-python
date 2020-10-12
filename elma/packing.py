from __future__ import annotations

import random
import struct
from typing import Union, Iterator, TYPE_CHECKING

import elma.models
from elma.constants import VERSION_ELMA
from elma.constants import VERSION_ACROSS
from elma.constants import END_OF_DATA_MARKER
from elma.constants import END_OF_FILE_MARKER
from elma.constants import END_OF_REPLAY_FILE_MARKER
from elma.utils import null_padded, crypt_top10

if TYPE_CHECKING:
    # defined here to avoid circular import at runtime
    LevelItem = Union[
        elma.models.Point,
        elma.models.Polygon,
        elma.models.Obj,
        elma.models.Picture,
        elma.models.Level
    ]

packers = {
    'Point': lambda point:
        struct.pack('d', point.x) + struct.pack('d', point.y),
    'Polygon': lambda polygon: b''.join([
        struct.pack('I', polygon.grass),
        struct.pack('I', len(polygon.points)),
    ] + [pack_level(point) for point in polygon.points]),
    'AcrossPolygon': lambda polygon: b''.join([
        struct.pack('I', len(polygon.points)),
    ] + [pack_level(point) for point in polygon.points]),
    'Obj': lambda obj: b''.join([
        pack_level(obj.point),
        struct.pack('I', obj.type),
        struct.pack('I', obj.gravity),
        struct.pack('I', obj.animation_number - 1)]),
    'AcrossObj': lambda obj: b''.join([
        pack_level(obj.point),
        struct.pack('I', obj.type)]),
    'Picture': lambda picture: b''.join([
        null_padded(picture.picture_name, 10),
        null_padded(picture.texture_name, 10),
        null_padded(picture.mask_name, 10),
        pack_level(picture.point),
        struct.pack('I', picture.distance),
        struct.pack('I', picture.clipping)])
}


def pack_level(item: LevelItem, is_elma: bool = True) -> bytes:
    """
    Pack a level-related item to its binary representation readable by
    Elasto Mania.
    """

    if not is_elma and type(item).__name__ in ['Polygon', 'Obj']:
        packer_name = 'Across' + type(item).__name__
    else:
        packer_name = type(item).__name__
    if packer_name in packers:
        return packers[packer_name](item)

    if isinstance(item, elma.models.Level):
        level = item
    else:
        raise NotImplementedError(f"Packing not implemented for type {type(item)}.")
    if is_elma:
        assert (level.version == VERSION_ELMA)
    else:
        assert (level.version == VERSION_ACROSS)

    polygon_checksum = sum([sum([point.x + point.y
                                 for point in polygon.points])
                            for polygon in level.polygons])
    object_checksum = sum([obj.point.x + obj.point.y + obj.type
                           for obj in level.objects])
    picture_checksum = sum([picture.point.x + picture.point.y
                            for picture in level.pictures]) if is_elma else 0
    collected_checksum = 3247.764325643 * (polygon_checksum +
                                           object_checksum +
                                           picture_checksum)
    if level.preserve_integrity_values:
        integrity_1, integrity_2, integrity_3, integrity_4 = level.integrity
    else:
        integrity_1 = collected_checksum
        integrity_2 = random.randint(0, 5871) + 11877 - collected_checksum
        integrity_3 = random.randint(0, 5871) + 11877 - collected_checksum
        integrity_4 = random.randint(0, 6102) + 12112 - collected_checksum
    assert ((integrity_3 - integrity_2) <= 5871)

    if is_elma:
        return b''.join([
            bytes(level.version, 'latin1'),
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
        ] + [bytes(chr(c), 'latin1')
             for c in crypt_top10(level.top10.to_buffer())] + [
            struct.pack('I', END_OF_FILE_MARKER),
        ])
    else:
        level_data = [
            bytes(level.version, 'latin1'),
            struct.pack('I', level.level_id),
            struct.pack('d', integrity_1),
            struct.pack('d', integrity_2),
            struct.pack('d', integrity_3),
            struct.pack('d', integrity_4),
            null_padded(level.name, 15),
            null_padded('', 44),
            struct.pack('d', len(level.polygons) + 0.4643643),
        ] + [pack_level(polygon, False) for polygon in level.polygons] + [
            struct.pack('d', len(level.objects) + 0.4643643),
        ] + [pack_level(obj, False) for obj in level.objects]

        if len(level.top10.single) > 0 or len(level.top10.multi) > 0:
            level_data += [
                struct.pack('I', END_OF_DATA_MARKER),
            ] + [bytes(chr(c), 'latin1')
                 for c in crypt_top10(level.top10.to_buffer())] + [
                struct.pack('I', END_OF_FILE_MARKER),
            ]
        return b''.join(level_data)


def unpack_level(packed_item: bytes) -> elma.models.Level:
    """
    Unpack a level-related item from its binary representation readable by
    Elasto Mania.
    """

    data = iter(packed_item)

    def munch(n: int, dataiter: Iterator[int] = data) -> bytes:
        return b''.join([bytes(chr(next(dataiter)), 'latin1')
                         for _ in range(n)])

    level = elma.models.Level()
    level.version = munch(5).decode('latin1')
    assert (level.version in [VERSION_ELMA, VERSION_ACROSS])
    is_elma = (level.version == VERSION_ELMA)

    if is_elma:
        munch(2)
    level.level_id = struct.unpack('I', munch(4))[0]
    if level.preserve_integrity_values:
        for _ in range(4):
            level.integrity.append(struct.unpack('d', munch(8))[0])
    else:
        munch(8 * 4)
    if is_elma:
        level.name = munch(51).split(b'\0')[0].decode('latin1')
        level.lgr = munch(16).split(b'\0')[0].decode('latin1')
        level.ground_texture = munch(10).split(b'\0')[0].decode('latin1')
        level.sky_texture = munch(10).split(b'\0')[0].decode('latin1')
    else:
        level.name = munch(15).split(b'\0')[0].decode('latin1')
        # Across header is zero padded to 100 chars
        munch(44)

    number_of_polygons = int(struct.unpack('d', munch(8))[0])
    for _ in range(number_of_polygons):
        grass = struct.unpack('I', munch(4))[0] if is_elma else False
        number_of_vertices = struct.unpack('I', munch(4))[0]
        points = []
        for __ in range(number_of_vertices):
            x = struct.unpack('d', munch(8))[0]
            y = struct.unpack('d', munch(8))[0]
            points.append(elma.models.Point(x, y))
        level.polygons.append(elma.models.Polygon(points, grass=grass))

    number_of_objects = int(struct.unpack('d', munch(8))[0])
    for _ in range(number_of_objects):
        x = struct.unpack('d', munch(8))[0]
        y = struct.unpack('d', munch(8))[0]
        object_type = struct.unpack('I', munch(4))[0]
        gravity = struct.unpack('I', munch(4))[0] if is_elma else 0
        animation_number = struct.unpack('I', munch(4))[0] + 1 if is_elma else 1
        level.objects.append(elma.models.Obj(elma.models.Point(x, y),
                                             object_type,
                                             gravity=gravity,
                                             animation_number=animation_number))

    if is_elma:
        number_of_pictures = int(struct.unpack('d', munch(8))[0])
        for _ in range(number_of_pictures):
            picture_name = munch(10).split(b'\0')[0].decode('latin1')
            texture_name = munch(10).split(b'\0')[0].decode('latin1')
            mask_name = munch(10).split(b'\0')[0].decode('latin1')
            x = struct.unpack('d', munch(8))[0]
            y = struct.unpack('d', munch(8))[0]
            distance = struct.unpack('I', munch(4))[0]
            clipping = struct.unpack('I', munch(4))[0]
            level.pictures.append(elma.models.Picture(elma.models.Point(x, y),
                                                      picture_name=picture_name,
                                                      texture_name=texture_name,
                                                      mask_name=mask_name,
                                                      distance=distance,
                                                      clipping=clipping))
        eod_marker = munch(4)
    else:
        # Across level has a top10 if it has been finished in Elma
        nextbyte = next(data, None)
        if nextbyte is None:
            return level
        else:
            eod_marker = munch(4, iter([nextbyte] + [b for b in munch(3)]))

    assert (struct.unpack('I', eod_marker)[0] == END_OF_DATA_MARKER)

    top10 = iter(crypt_top10(munch(688)))
    for top10_block in ['single', 'multi']:
        times = []
        kuskis1 = []
        kuskis2 = []
        time_count = struct.unpack('I', munch(4, top10))[0]
        for _ in range(10):
            times.append(struct.unpack('I', munch(4, top10))[0])
        for _ in range(10):
            kuskis1.append(munch(15, top10).split(b'\0')[0].decode('latin1'))
        for _ in range(10):
            kuskis2.append(munch(15, top10).split(b'\0')[0].decode('latin1'))
        times = times[:time_count]
        kuskis1 = kuskis1[:time_count]
        kuskis2 = kuskis2[:time_count]
        if top10_block == 'single':
            level.top10.single = [elma.models.Top10Time(t, kuskis1[i], kuskis2[i])
                                  for i, t in enumerate(times)
                                  if (t > 0 and len(kuskis1[i]) > 0)]
        else:
            level.top10.multi = [elma.models.Top10Time(t, kuskis1[i], kuskis2[i], True)
                                 for i, t in enumerate(times)
                                 if (t > 0 and len(kuskis1[i]) > 0 and
                                     len(kuskis2[i]) > 0)]

    assert (struct.unpack('I', munch(4))[0] == END_OF_FILE_MARKER)
    return level


def unpack_replay(packed_item: bytes) -> elma.models.Replay:
    """
    Unpack a replay-related item from its binary representation readable by
    Elasto Mania.
    """

    data = iter(packed_item)

    def munch(n: int) -> bytes:
        return b''.join([bytes(chr(next(data)), 'latin1') for _ in range(n)])

    def read_int32() -> int:
        return struct.unpack('i', munch(4))[0]

    def read_uint32() -> int:
        return struct.unpack('I', munch(4))[0]

    def read_int16() -> int:
        return struct.unpack('h', munch(2))[0]

    def read_uint8() -> int:
        return struct.unpack('B', munch(1))[0]

    def read_float() -> float:
        return struct.unpack('f', munch(4))[0]

    def read_double() -> float:
        return struct.unpack('d', munch(8))[0]

    replay = elma.models.Replay()

    number_of_replay_frames = read_int32()
    munch(4)
    replay.is_multi = bool(read_int32())
    replay.is_flagtag = bool(read_int32())
    replay.level_id = read_uint32()
    replay.level_name = munch(12).split(b'\0')[0].decode('latin1')
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

        frame = elma.models.Frame()
        frame.position = elma.models.Point(x, y)
        frame.left_wheel_position = elma.models.Point(left_wheel_x, left_wheel_y)
        frame.right_wheel_position = elma.models.Point(right_wheel_x, right_wheel_y)
        frame.head_position = elma.models.Point(head_x, head_y)
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
        info = read_int16()
        event_type = read_int16()
        event_sound_volume = read_float()
        event: elma.models.Event
        if event_type == 0:
            event = elma.models.ObjectTouchEvent()
            event.object_number = info
        elif event_type == 5:
            event = elma.models.TurnEvent()
        elif event_type == 7:
            event = elma.models.LeftVoltEvent()
        elif event_type == 6:
            event = elma.models.RightVoltEvent()
        elif event_type == 1:
            event = elma.models.GroundTouchEvent()
            event.event_sound_volume = event_sound_volume
        elif event_type == 4:
            event = elma.models.AppleTouchEvent()
        else:
            raise NotImplementedError(f"Event type {event_type} not implemented.")

        event.time = event_time
        replay.events.append(event)

    last_frame_time = len(replay.frames)/30.0
    last_event_time = (0.0 if len(replay.events) == 0 else
                       replay.events[-1].time * (0.001/(0.182*0.0024)))

    replay.is_finished = False
    # Potentially finished, if replay ends in a touch event
    if (len(replay.events) > 0 and
        (last_frame_time <= last_event_time + 1/30.0) and
            isinstance(replay.events[-1], (elma.models.ObjectTouchEvent, elma.models.AppleTouchEvent))):

        if isinstance(replay.events[-1], elma.models.ObjectTouchEvent):
            if (len(replay.events) >= 2 and
                isinstance(replay.events[-2], elma.models.ObjectTouchEvent) and
                    replay.events[-2].time != replay.events[-1].time):
                # Probably ended at flower, but not all apples were taken
                replay.is_finished = False
            else:
                # False positives are possible (e.g., dying to killer)
                replay.is_finished = True
        elif (len(replay.events) >= 3 and
              isinstance(replay.events[-1], elma.models.AppleTouchEvent)):
            end_apple_count = sum(1 for e in replay.events
                                  if isinstance(e, elma.models.AppleTouchEvent) and
                                  e.time == replay.events[-1].time)
            possible_flower_event = replay.events[-1 - 2*end_apple_count]
            if (isinstance(possible_flower_event, elma.models.ObjectTouchEvent) and
                    possible_flower_event.time == replay.events[-1].time):
                # Apple(s) and flower taken at the same time
                replay.is_finished = True

    replay.time = last_event_time if replay.is_finished else last_frame_time
    return replay


def pack_replay(item: Union[elma.models.Event, elma.models.Replay]) -> bytes:
    """
    Pack a replay-related item to its binary representation readable by
    Elasto Mania.
    """

    if isinstance(item, elma.models.ObjectTouchEvent):
        return (struct.pack('d', item.time) +
                struct.pack('I', item.object_number) +
                struct.pack('f', 0))

    if isinstance(item, elma.models.TurnEvent):
        return (struct.pack('d', item.time) +
                struct.pack('h', -1) +
                struct.pack('h', 5) +
                struct.pack('f', 0.99))

    if isinstance(item, elma.models.LeftVoltEvent):
        return (struct.pack('d', item.time) +
                struct.pack('h', -1) +
                struct.pack('h', 7) +
                struct.pack('f', 0.99))

    if isinstance(item, elma.models.RightVoltEvent):
        return (struct.pack('d', item.time) +
                struct.pack('h', -1) +
                struct.pack('h', 6) +
                struct.pack('f', 0.99))

    if isinstance(item, elma.models.GroundTouchEvent):
        return (struct.pack('d', item.time) +
                struct.pack('h', -1) +
                struct.pack('h', 1) +
                struct.pack('f', item.event_sound_volume))

    if isinstance(item, elma.models.AppleTouchEvent):
        return (struct.pack('d', item.time) +
                struct.pack('h', -1) +
                struct.pack('h', 4) +
                struct.pack('f', 0.99))
    if isinstance(item, elma.models.Replay):
        replay = item
    else:
        raise NotImplementedError(f"Packing not implemented for type {type(item)}")

    name = null_padded(replay.level_name, 12)
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
