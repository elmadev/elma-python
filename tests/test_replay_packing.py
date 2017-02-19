from elma.packing import pack_replay
from elma.packing import unpack_replay
import unittest


class TestReplayPacking(unittest.TestCase):

    def test_packing(self):
        with open('tests/files/test.rec', 'rb') as f:
            packed_replay = f.read()
            replay = unpack_replay(packed_replay)
            self.assertEqual(False, replay.is_multi)
            self.assertEqual(False, replay.is_flagtag)
            self.assertEqual(2958928182, replay.level_id)
            self.assertEqual(b'sig0957.lev', replay.level_name)
            self.assertEqual(857, len(replay.frames))
            self.assertEqual(83, len(replay.events))
            repacked_replay = pack_replay(replay)
            self.assertEqual(packed_replay, repacked_replay)
