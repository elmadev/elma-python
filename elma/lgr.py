from PIL import Image
from elma.constants import LGR_DEFAULT_PALETTE
from elma.constants import LGR_END_OF_FILE
from elma.constants import LGR_FOOD_NAME
from elma.constants import LGR_NOT_IN_PICTURES_LST
from elma.constants import LGR_OBJECT_NAME
from elma.constants import LGR_PCX_PADDING
from elma.constants import LGR_PICTURES_LST_ID
from elma.utils import null_padded
import io
import re
import struct


class LGR_Image(object):
    """
    Represents one entry in an LGR file.

    All entries in the LGR file have a name and an image (in .pcx format). Most
    images have extra information stored in a pictures.lst file contained
    within the LGR file. However, some of the special images (bike images and
    qkiller, qexit, qframe, qcolors and qgrass) are not included in the
    pictures.lst file and so do not have this additional information.

    Attributes:
        name (string): The name of the item in the LGR file, excluding pcx.
            e.g. "barrel"
        img (Image): Image object pointing to the image to be used
            (PIL.Image.open(file))
            http://pillow.readthedocs.io/en/3.1.x/reference/Image.html
        image_type (int): The type of image. Should be one of:
            LGR_Image.PICTURE, LGR_Image.TEXTURE, LGR_Image.MASK. Only used if
            **is_in_pictures_lst()=True**
        default_distance (int): The default z-ordering distance of a picture or
            texture. Should be in the range 1-999. Only used **if
            is_in_pictures_lst()=True**
        default_clipping (int): The default clipping of a picture or texture.
            Should be one of: LGR_Image.CLIPPING_U, LGR_Image.CLIPPING_G,
            LGR_Image.CLIPPING_S. Only used if **is_in_pictures_lst()=True**
        transparency (int): The pixel corresponding to the color or item in a
        palette that should be transperant. Should be one of:
            LGR_Image.TRANSPARENCY_PAL_ZERO, LGR_Image.TRANSPARENCY_TOPLEFT,
            LGR_Image.TRANSPARENCY_TOPRIGHT, LGR_Image.TRANSPARENCY_BOTTOMLEFT,
            LGR_Image.TRANSPARENCY_BOTTOMRIGHT. Only used if
            **is_in_pictures_lst()=True**.  TRANSPARENCY_PAL_ZERO indicates the
            the palette index 0 is selected as the transparent color.
        padding (int[7]): Each LGR entry has 7 bytes of padding that are
            unused. This can in theory be used to store extra information.
    """

    CLIPPING_U = 0
    CLIPPING_G = 1
    CLIPPING_S = 2
    PICTURE = 100
    TEXTURE = 101
    MASK = 102
    TRANSPARENCY_PAL_ZERO = 11
    TRANSPARENCY_TOPLEFT = 12
    TRANSPARENCY_TOPRIGHT = 13
    TRANSPARENCY_BOTTOMLEFT = 14
    TRANSPARENCY_BOTTOMRIGHT = 15

    def is_in_pictures_lst(self):
        """
        Determines whether image with the given name appears in pictures.lst
        (i.e. has the extra variables image_type, default_distance,
        default_clipping, transparency)
        Returns True if the image appears in pictures.lst, meaning the extra
        variables may be used. See also is_special().
        """
        return self.name.lower() not in LGR_NOT_IN_PICTURES_LST

    def get_palette(self):
        """
        Returns the palette of the image in the format [r, g, b, ...], or None
        if the image has no palette.
        """
        return self.img.getpalette()

    def put_palette(self, palette):
        """
        Sets the image's palette. Does NOT convert image colors. Can only be
        used on images that are palette-based.
        """
        self.img.putpalette(palette)

    def convert_palette_image(self, palette_info=LGR_DEFAULT_PALETTE,
                              dither=False):
        """
        Converts the current image into an appropriate palette
        format, keeping the color as close to the original as possible.

        Arguments:
            palette_info (byte[768]): The palette to apply to the image. May be
                obtained from LGR_Image.get_palette(). The default is the
                default palette from default.lgr.
            dither (bool): Whether to dither the image during conversion
        """
        palette = Image.new('P', (1, 1))
        palette.putpalette(palette_info[:], 'RGB')
        self.img = self.img._new(
            self.img.convert(
                mode='RGB').im.convert('P', dither, palette.im))

    def is_valid_palette_image(self):
        """
        Returns True if image has a palette of 256 rgb values.
        """
        return (self.img.mode == 'P' and
                self.img.palette.mode == 'RGB' and
                len(self.get_palette()) == 768)

    def save_PCX(self, filename):
        """
        Writes the image as a .pcx file to `filename`.
        """
        self.img.save(filename, 'pcx')

    def is_qup_qdown(self):
        """
        Checks if the current object name qualifies as a qup_ or qdown_ object.
        """
        name_lower = self.name.lower()
        return name_lower[:4] == "qup_" or name_lower[:6] == "qdown_"

    def is_food(self):
        """
        Checks if the current object name is qfood*.
        """
        return self.name.lower() in LGR_FOOD_NAME

    def is_object(self):
        """
        Checks if the current name is a recognized object (qfood*, qexit,
        qkiller)
        """
        return (self.name.lower() in LGR_OBJECT_NAME)

    def is_special(self):
        """
        Checks if the current object is a special object (i.e. treated
        differently from normal images, so that image_type, default_distance,
        default_clipping, trasparency either don't exist or are ignored by
        elma.exe.
        """
        return (not self.is_in_pictures_lst() or
                self.is_food() or
                self.is_qup_qdown())

    def __init__(self, name, img=None, image_type=PICTURE,
                 default_distance=500, default_clipping=CLIPPING_S,
                 transparency=TRANSPARENCY_TOPLEFT, padding=LGR_PCX_PADDING):
        self.name = name
        self.img = img
        self.padding = padding
        self.image_type = image_type
        self.default_distance = default_distance
        self.default_clipping = default_clipping
        self.transparency = transparency

    def __repr__(self):
        if(self.is_in_pictures_lst()):
            return (('LGR_Image(name: %s, img: %s, image_type: %s, ' +
                     'default_distance: %s, default_clipping: %s, ' +
                     'transparency: %s, padding: %s)') %
                    (self.name, self.img, self.image_type,
                     self.default_distance, self.default_clipping,
                     self.transparency, self.padding))
        return (('LGR_Image(name: %s, img: %s, padding: %s)') %
                (self.name, self.img, self.padding))

    def __eq__(self, other_picture):
        if(self.is_in_pictures_lst()):
            return (self.name == other_picture.name and
                    self.img.mode == other_picture.img.mode and
                    self.img.size == other_picture.img.size and
                    self.get_palette() == other_picture.get_palette() and
                    self.img.tobytes() == other_picture.img.tobytes() and
                    self.image_type == other_picture.image_type and
                    self.default_distance == other_picture.default_distance and
                    self.default_clipping == other_picture.default_clipping and
                    self.transparency == other_picture.transparency and
                    self.padding == other_picture.padding)
        return (self.name == other_picture.name and
                self.img.mode == other_picture.img.mode and
                self.img.size == other_picture.img.size and
                self.get_palette() == other_picture.get_palette() and
                self.img.tobytes() == other_picture.img.tobytes() and
                self.padding == other_picture.padding)


class LGR(object):
    """
    Represent an LGR file

    Attributes:
        images (list): A list of LGR_Image objects contained in the lgr file
        palette: Palette to use in the LGR file. Should be an array 768 bytes
            long in the format [r,g,b,r,g,b,...]. Inputting -1 will use the
            default palette from default.lgr
    """

    def __init__(self, palette=None):
        self.images = []
        if not palette:
            palette = LGR_DEFAULT_PALETTE[:]
        self.palette = palette

    def find_LGR_Image(self, filename):
        """
        Searches for an LGR_Image with the name of "filename" and returns the
        index number in the list of LGR.images. Case-insensitive. Returns
        ValueError if not found.
        """
        filename = filename.lower()
        for i, image in enumerate(self.images):
            if image.name.lower() == filename:
                return i
        raise ValueError('\'%s\' not in LGR.images' % filename)

    def __repr__(self):
        return 'LGR(images: %s)' % self.images


def unpack_LGR(data):
    """
    Opens an LGR file when you pass raw data or a filename
    """

    def get_int32(loc):
        return struct.unpack('<I', data[loc:loc+4])[0]

    if(type(data).__name__ == "str"):
        with open(data, 'rb') as f:
            data = f.read()

    lgr = LGR()
    pictures = []  # temp list to retain order of files by x instead of l

    assert(data[0:5] == b'LGR12')
    x = get_int32(5)
    assert(get_int32(9) == LGR_PICTURES_LST_ID)
    l = get_int32(13)

    for i in range(l):
        pictures.append(LGR_Image(
            name=data[17+10*i:17+10*i+10].rstrip(b'\0').decode('latin1'),
            img=None,
            image_type=get_int32(17+10*l+4*i),
            default_distance=get_int32(17+14*l+4*i),
            default_clipping=get_int32(17+18*l+4*i),
            transparency=get_int32(17+22*l+4*i),
            padding=LGR_PCX_PADDING))

    sp = 17+l*26

    found_palette = False
    term = re.compile(b'.pcx\0', re.IGNORECASE)
    for i in range(x):
        pcx_name = data[sp:sp+13]
        pcx_name = pcx_name[:term.search(pcx_name).start()].decode('latin1')
        lst_pcx_match = False
        pcx_padding = [int.from_bytes(data[sp+12+1+k:sp+12+1+k+1],
                                      byteorder='little', signed=False)
                       for k in range(7)]
        pcx_len = get_int32(sp+20)
        pcx_img = Image.open(io.BytesIO(data[sp+24:sp+24+pcx_len]))
        if pcx_name.lower() == 'q1bike':
            lgr.palette = pcx_img.getpalette()
            found_palette = True
        for obj in pictures:
            if(obj.name.lower() == pcx_name.lower()):
                obj.img = pcx_img
                obj.padding = pcx_padding
                lgr.images.append(obj)
                lst_pcx_match = True
                break
        if not lst_pcx_match:
            lgr.images.append(LGR_Image(
                name=pcx_name,
                img=pcx_img,
                padding=pcx_padding))
        sp = sp+24+pcx_len
    if not found_palette and lgr.images:
        lgr.images[0].get_palette()

    assert(get_int32(sp) == LGR_END_OF_FILE)

    return lgr


def pack_LGR(lgr):
    """
    Converts LGR object into its binary representation to be saved as an lgr
    file.
    """

    def to_int32(val):
        return struct.pack('<I', val)

    l = 0
    l_name = []
    l_image_type = []
    l_default_distance = []
    l_default_clipping = []
    l_transparency = []
    x = []
    for obj in lgr.images:
        if(obj.is_in_pictures_lst()):
            l = l+1
            l_name.extend([null_padded(obj.name, 8), b'\0\0'])
            l_image_type.append(to_int32(obj.image_type))
            l_default_distance.append(to_int32(obj.default_distance))
            l_default_clipping.append(to_int32(obj.default_clipping))
            l_transparency.append(to_int32(obj.transparency))
        with io.BytesIO() as f:
            obj.save_PCX(f)
            x_len = f.tell()
            f.seek(0)
            x.extend([
                null_padded('%s.pcx' % obj.name, 13),
                bytes(obj.padding),
                to_int32(x_len),
                f.read()])

    return b"".join([
        b'LGR12',
        to_int32(len(lgr.images)),
        to_int32(LGR_PICTURES_LST_ID),
        to_int32(l),
        b''.join(l_name),
        b''.join(l_image_type),
        b''.join(l_default_distance),
        b''.join(l_default_clipping),
        b''.join(l_transparency),
        b''.join(x),
        to_int32(LGR_END_OF_FILE)])
