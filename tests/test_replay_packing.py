from pathlib import Path
import tempfile

from elma.models import Replay
import unittest


class TestReplayPacking(unittest.TestCase):

    def test_packing(self):
        file = Path('tests/files/test.rec')
        packed_replay = file.read_bytes()
        replay = Replay.load(file)
        self.assertEqual(False, replay.is_multi)
        self.assertEqual(False, replay.is_flagtag)
        self.assertEqual(2958928182, replay.level_id)
        self.assertEqual(b'sig0957.lev', replay.level_name)
        self.assertEqual(857, len(replay.frames))
        self.assertEqual(83, len(replay.events))
        with tempfile.TemporaryDirectory() as tmp_dir:
            saved_file = Path(tmp_dir) / "test.rec"
            replay.save(saved_file)
            self.assertEqual(packed_replay, saved_file.read_bytes())

    def test_packing_nonstandard_format(self):
        # this replay uses the event info field in a non-standard way
        # in the original elma it is always -1, except for the object touch events
        file = Path('tests/files/test_nonstandard_rec_format.rec')

        replay = Replay.load(file)
        with tempfile.TemporaryDirectory() as tmp_dir:
            saved_file = Path(tmp_dir) / "test.rec"
            replay.save(saved_file)
            re_unpacked_replay = Replay.load(saved_file)

        def check_replay_values(rec):
            self.assertEqual(False, rec.is_multi)
            self.assertEqual(False, rec.is_flagtag)
            self.assertEqual(132439557, rec.level_id)
            self.assertEqual(b'aint01.lev', rec.level_name)
            self.assertEqual(458, len(rec.frames))
            self.assertEqual(42, len(rec.events))

        check_replay_values(replay)
        check_replay_values(re_unpacked_replay)

        # comparing packed and repacked replays directly doesn't work,
        # because of the non-standard packing in the original replay
        # therefore events and frames are compared individually
        for event, event2 in zip(replay.events, re_unpacked_replay.events):
            self.assertEqual(event.time, event2.time)
            self.assertEqual(type(event), type(event2))

        for frame, frame2 in zip(replay.frames, re_unpacked_replay.frames):
            self.assertEqual(frame.position, frame2.position)
            self.assertEqual(frame.left_wheel_position, frame2.left_wheel_position)
            self.assertEqual(frame.right_wheel_position, frame2.right_wheel_position)
            self.assertEqual(frame.head_position, frame2.head_position)
            self.assertEqual(frame.rotation, frame2.rotation)
            self.assertEqual(frame.left_wheel_rotation, frame2.left_wheel_rotation)
            self.assertEqual(frame.right_wheel_rotation, frame2.right_wheel_rotation)
            self.assertEqual(frame.is_gasing, frame2.is_gasing)
            self.assertEqual(frame.is_turned_right, frame2.is_turned_right)
            self.assertEqual(frame.spring_sound_effect_volume, frame2.spring_sound_effect_volume)
