import unittest
import elma


class TestUtils(unittest.TestCase):

    def test_null_padding(self):
        string = 'string longer than length parameter'
        self.assertEquals('string lon',
                          elma.utils.null_padded(string, 10))
        string = 'string shorter than length parameter'
        self.assertEquals(string + ('\0' * 4),
                          elma.utils.null_padded(string, 40))
        string = 'string same length as length parameter'
        self.assertEquals(string,
                          elma.utils.null_padded(string, 38))
