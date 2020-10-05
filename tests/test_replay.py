from elma.packing import unpack_replay
import unittest


class TestReplay(unittest.TestCase):

    def test_replay_time(self):
        with open('tests/files/test.rec', 'rb') as f:
            replay = unpack_replay(f.read())
            self.assertEqual(True, replay.is_finished)
            self.assertEqual(28.545999999997303,
                             replay.time)
