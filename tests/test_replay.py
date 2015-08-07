from elma.packing import unpack_replay
import unittest


class TestReplay(unittest.TestCase):

    def test_get_exact_duration_in_seconds(self):
        with open('tests/test.rec', 'rb') as f:
            replay = unpack_replay(f.read())
            self.assertEqual(28.5459999999973,
                             replay.get_exact_duration_in_seconds())
