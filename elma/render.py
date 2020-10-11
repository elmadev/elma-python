from __future__ import annotations

from typing import Tuple, Optional
from PIL import Image, ImageDraw
import elma.models
from elma.constants import OBJECT_RADIUS


class LevelRenderer:

    DEFAULT_WIDTH = 1920
    DEFAULT_HEIGHT = 1080
    DEFAULT_PADDING = 10

    def __init__(self,
                 level: elma.models.Level,
                 max_width: Optional[int] = DEFAULT_WIDTH,
                 max_height: Optional[int] = DEFAULT_HEIGHT,
                 padding: int = DEFAULT_PADDING) -> None:
        """
        Render image of a level

        Args:
            level: Level object to render
            max_width: optional maximum width of the rendered image in pixels or None
            max_height: optional maximum height of the rendered image in pixels or None
            padding: space around the image in pixels
        """
        self.level = level
        self.padding = padding
        self.scale = None
        self._min_x, self._max_x, self._min_y, self._max_y = level.bounding_box()
        # use defaults if both size limits are None
        if max_width is None and max_height is None:
            max_width = self.DEFAULT_WIDTH
            max_height = self.DEFAULT_HEIGHT
        elif (max_width is not None and max_width <= 0) or (max_height is not None and max_height <= 0):
            raise ValueError(f"Non-positive size limit (width = {max_width}, height = {max_height})")
        if max_width:
            width_scale = (max_width - 2 * padding) / (self._max_x - self._min_x)
            self.scale = width_scale
        if max_height:
            height_scale = (max_height - 2 * padding) / (self._max_y - self._min_y)
            if self.scale is not None:
                self.scale = min(self.scale, height_scale)
            else:
                self.scale = height_scale
        self.colors = {
            "sky": (149, 184, 209),
            "ground": (13, 59, 102),
            "apple": (163, 22, 33),
            "killer": (0, 0, 0),
            "flower": (255, 255, 255),
            "start": (254, 198, 1),
        }

    @classmethod
    def with_scale(cls, level: elma.models.Level, scale: float, padding: int = DEFAULT_PADDING) -> LevelRenderer:
        """
        Create a LevelRenderer with a constant scaling factor.

        Args:
            level: Level object to render
            scale: scaling factor to convert level coordinates to pixels
            padding: space around the image in pixels

        Returns:
            LevelRenderer instance
        """
        renderer = cls(level=level, padding=padding)
        renderer.scale = scale
        return renderer

    @property
    def image_width(self) -> int:
        """
        The width of the image in pixels.
        """
        return round((self._max_x - self._min_x) * self.scale + 2 * self.padding)

    @property
    def image_height(self) -> int:
        """
        The height of the image in pixels.
        """
        return round((self._max_y - self._min_y) * self.scale + 2 * self.padding)

    @property
    def image_size(self) -> Tuple[int, int]:
        """
        The width and height of the image in pixels.
        """
        return self.image_width, self.image_height

    def render(self, render_objects: bool = True) -> Image:
        """
        Render image of the level

        Args:
            render_objects: render both objects and polygons if True,
                else render only polygons

        Returns:
            image of the level
        """
        im = Image.new('RGB', self.image_size, color=self.colors["sky"])
        self._render_polygons(im)
        if render_objects:
            self._render_objects(im)
        return im

    def show(self, render_objects: bool = True) -> None:
        """
        Show image of the level

        Args:
            render_objects: render both objects and polygons if True,
                else render only polygons
        """
        im = self.render(render_objects=render_objects)
        im.show()

    def to_pixel_coordinates(self, x: float, y: float) -> Tuple[int, int]:
        """
        Convert a level coordinate to image coordinate (pixels).

        Args:
            x: level x coordinate
            y: level y coordinate

        Returns:
            image coordinate (x, y) in pixels
        """
        x_pixel = round(self.scale * (x - self._min_x) + self.padding)
        y_pixel = round(self.scale * (y - self._min_y) + self.padding)
        return x_pixel, y_pixel

    def to_level_coordinates(self, x_pixel: int, y_pixel: int) -> Tuple[float, float]:
        """
        Convert an image coordinate (pixels) to a level coordinate.

        Note that this is an approximation due to rounding errors.

        Args:
            x_pixel: image x coordinate in pixels
            y_pixel: image y coordinate in pixels

        Returns:
            approximate level coordinate (x, y)

        """
        x = (x_pixel - self.padding) / self.scale + self._min_x
        y = (y_pixel - self.padding) / self.scale + self._min_y
        return x, y

    def polygon_mask(self) -> Image:
        """
        Returns a binary mask of all non-grass polygons of the level.
        """
        polygons = sorted(self.level.ground_polygons, key=lambda p: p.area(), reverse=True)
        mask_color = 0
        if not polygons[0].is_filled():
            mask_color = 1
        im = Image.new('1', self.image_size, color=mask_color)
        canvas = ImageDraw.Draw(im)
        for polygon in polygons:
            poly = [self.to_pixel_coordinates(p.x, p.y) for p in polygon.points]
            canvas.polygon(poly, fill=polygon.is_filled())
        return im

    def object_mask(self) -> Image:
        """
        Returns a binary mask of a level object.
        """
        size = round(2 * OBJECT_RADIUS * self.scale)
        im = Image.new('1', (size + 1, size + 1))
        canvas = ImageDraw.Draw(im)
        mask_color = 1
        canvas.ellipse((0, 0, size, size), fill=mask_color)
        return im

    def _render_polygons(self, im: Image) -> None:
        """
        Add rendered polygons to the given image.
        """
        polygons = self.polygon_mask()
        im.paste(self.colors["ground"], mask=polygons)

    def _render_objects(self, im: Image) -> None:
        """
        Add rendered level objects to the given image.
        """
        for obj in self.level.objects:
            x = obj.point.x - OBJECT_RADIUS
            y = obj.point.y - OBJECT_RADIUS
            position = self.to_pixel_coordinates(x, y)
            if obj.type == elma.models.Obj.FLOWER:
                color = self.colors["flower"]
            elif obj.type == elma.models.Obj.FOOD:
                color = self.colors["apple"]
            elif obj.type == elma.models.Obj.KILLER:
                color = self.colors["killer"]
            elif obj.type == elma.models.Obj.START:
                color = self.colors["start"]
            else:
                raise NotImplementedError(f"Object type {obj.type} not implemented")
            im.paste(color, position, self.object_mask())
