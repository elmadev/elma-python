import unittest
import elma.utils


class TestUtils(unittest.TestCase):

    def test_null_padding(self):
        string = 'string longer than length parameter'
        self.assertEqual('string lon',
                         elma.utils.null_padded(string, 10).decode('latin1'))
        string = 'string shorter than length parameter'
        self.assertEqual(string + ('\0' * 4),
                         elma.utils.null_padded(string, 40).decode('latin1'))
        string = 'string same length as length parameter'
        self.assertEqual(string,
                         elma.utils.null_padded(string, 38).decode('latin1'))
