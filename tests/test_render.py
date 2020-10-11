import unittest
from PIL import Image
from elma.packing import unpack_level


class TestLevelRender(unittest.TestCase):
    def load_level(self, level_file):
        with open(level_file, 'rb') as f:
            level = unpack_level(f.read())
        return level

    def test_image(self):
        level = self.load_level('tests/files/qwquu039.lev')
        im_rendered = level.as_image(max_width=2000, max_height=None, padding=10)
        im = Image.open('tests/files/qwquu039.png').convert('RGB')
        self.assertEqual(im_rendered, im)
        im_rendered_polygons = level.as_image(max_width=2000, max_height=None, padding=10, render_objects=False)
        im_polygons = Image.open('tests/files/qwquu039_polygons.png').convert('RGB')
        self.assertEqual(im_rendered_polygons, im_polygons)

    def test_image_size(self):
        level = self.load_level('tests/files/qwquu039.lev')
        self.assertEqual(level.as_image(max_width=200, padding=10).size, (200, 109))
        self.assertEqual(level.as_image(max_width=200, padding=20).size, (200, 120))
        self.assertEqual(level.as_image(max_height=200, padding=10).size, (382, 200))
        self.assertEqual(level.as_image(max_width=200, max_height=200, padding=10).size, (200, 109))
        self.assertEqual(level.as_image(scale=10, padding=10).size, (1678, 844))
        self.assertEqual(level.as_image(scale=10, padding=20).size, (1698, 864))
        self.assertEqual(level.as_image(scale=20, padding=10).size, (3337, 1669))
        self.assertEqual(level.as_image(scale=20, padding=20).size, (3357, 1689))


if __name__ == '__main__':
    unittest.main()
