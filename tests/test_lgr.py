from elma.lgr import unpack_LGR
from elma.lgr import pack_LGR
from elma.lgr import LGR_Image
import elma.error
from elma.error import check_LGR_error
from elma.constants import LGR_DEFAULT_PALETTE
import unittest
from PIL import Image
from PIL import ImageDraw
import os


class TestLGR(unittest.TestCase):
    def test_LGR_Image(self):
        # Test get_palette()
        with Image.open('tests/files/barrel.pcx') as f:
            lgrimg = LGR_Image('barrel', f)
            self.assertEqual(lgrimg.get_palette(), LGR_DEFAULT_PALETTE)

        # Test is_in_pictures_lst(), is_qup_qdown(), is_food(), is_special()
        lgrimg = LGR_Image('barrel')
        self.assertEqual(lgrimg.is_in_pictures_lst(), True)
        self.assertEqual(lgrimg.is_qup_qdown(), False)
        self.assertEqual(lgrimg.is_food(), False)
        self.assertEqual(lgrimg.is_special(), False)
        lgrimg.name = "q1body"
        self.assertEqual(lgrimg.is_in_pictures_lst(), False)
        self.assertEqual(lgrimg.is_qup_qdown(), False)
        self.assertEqual(lgrimg.is_food(), False)
        self.assertEqual(lgrimg.is_special(), True)
        lgrimg.name = "Q1BODY"
        self.assertEqual(lgrimg.is_in_pictures_lst(), False)
        self.assertEqual(lgrimg.is_qup_qdown(), False)
        self.assertEqual(lgrimg.is_food(), False)
        self.assertEqual(lgrimg.is_special(), True)
        lgrimg.name = "qFoOd5"
        self.assertEqual(lgrimg.is_in_pictures_lst(), True)
        self.assertEqual(lgrimg.is_qup_qdown(), False)
        self.assertEqual(lgrimg.is_food(), True)
        self.assertEqual(lgrimg.is_special(), True)
        lgrimg.name = "qUp_xS"
        self.assertEqual(lgrimg.is_in_pictures_lst(), True)
        self.assertEqual(lgrimg.is_qup_qdown(), True)
        self.assertEqual(lgrimg.is_food(), False)
        self.assertEqual(lgrimg.is_special(), True)

        # Test is_valid_palette_image()
        with Image.open('tests/files/barrel.pcx') as f:
            lgrimg = LGR_Image('barrel', f)
            self.assertEqual(lgrimg.is_valid_palette_image(), True)
        with Image.open('tests/files/barrel.bmp') as f:
            lgrimg = LGR_Image('barrel', f)
            self.assertEqual(lgrimg.is_valid_palette_image(), True)
        with Image.open('tests/files/barrelgrayscale.bmp') as f:
            lgrimg = LGR_Image('barrel', f)
            self.assertEqual(lgrimg.is_valid_palette_image(), False)
        with Image.open('tests/files/barrelrgb.png') as f:
            lgrimg = LGR_Image('barrel', f)
            self.assertEqual(lgrimg.is_valid_palette_image(), False)
        with Image.open('tests/files/barrel_partial_palette.pcx') as f:
            lgrimg = LGR_Image('barrel', f)
            self.assertEqual(lgrimg.is_valid_palette_image(), True)

        # Test convert_palette_image()
        with Image.open('tests/files/barrelrgb.png') as f:
            lgrimg = LGR_Image('barrel', f)
            lgrimg.img = lgrimg.convert_palette_image(
                palette_info=LGR_DEFAULT_PALETTE,
                dither=False)
            os.makedirs(
                os.path.dirname("tests/files/result/barrelrgb2pal.pcx"),
                exist_ok=True)
            lgrimg.save_PCX("tests/files/result/barrelrgb2pal.pcx")
            with Image.open('tests/files/barrel.pcx') as g:
                self.assertEqual(lgrimg.img.mode, g.mode)
                self.assertEqual(lgrimg.img.size, g.size)
                self.assertEqual(lgrimg.img.getpalette(), g.getpalette())
                self.assertEqual(lgrimg.img.tobytes(), g.tobytes())
        with Image.open('tests/files/woman.png') as f:
            lgrimg = LGR_Image('woman', f)
            lgrimg.img = lgrimg.convert_palette_image(
                LGR_DEFAULT_PALETTE, True)
            lgrimg.save_PCX('tests/files/result/woman.pcx')
            self.assertEqual(lgrimg.img.getpalette(), LGR_DEFAULT_PALETTE)
        with Image.open('tests/files/barrel_partial_palette.pcx') as f:
            lgrimg = LGR_Image('barrel', f)
            lgrimg.img = lgrimg.convert_palette_image(
                palette_info=LGR_DEFAULT_PALETTE, dither=False)
            lgrimg.save_PCX(
                "tests/files/result/barrel_partial_to_full_palette.pcx")
            with Image.open('tests/files/barrel.pcx') as g:
                self.assertEqual(lgrimg.img.mode, g.mode)
                self.assertEqual(lgrimg.img.size, g.size)
                self.assertEqual(lgrimg.img.getpalette(), g.getpalette())
                self.assertEqual(lgrimg.img.tobytes(), g.tobytes())

        # Test get_default_palette
        self.assertEqual(LGR_Image.get_default_palette(), LGR_DEFAULT_PALETTE)

        # Test packing and unpacking
        lgr1 = unpack_LGR('tests/files/default.lgr')
        with open('tests/files/result/default.lgr', 'wb') as f:
            f.write(pack_LGR(lgr1))
        # not comparing binaries here because the script changes pcx header &
        # compresses a bit better than original .pcx files
        lgr2 = unpack_LGR('tests/files/result/default.lgr')
        self.assertEqual(lgr1.palette, lgr2.palette)
        for k in range(len(lgr1.images)):
            self.assertEqual(lgr1.images[k], lgr2.images[k])

        # Test LGR.find_LGR_Image()
        index = lgr1.find_LGR_Image("q2THiGh")
        self.assertEqual(index, 3)  # 4th entry in default.lgr is Q2THIGH.pcx

        # TEST ERROR CHECKING
        self.assertEqual(check_LGR_error(lgr1), [])
        # ERR_LGR_INVALID_PALETTE
        lgr1.palette[0] = 300
        self.assertEqual(check_LGR_error(lgr1)[0][0],
                         elma.error.ERR_LGR_INVALID_PALETTE)
        lgr1.palette[0] = -10
        self.assertEqual(check_LGR_error(lgr1)[0][0],
                         elma.error.ERR_LGR_INVALID_PALETTE)
        lgr1.palette[0] = 0
        lgr1.palette.append([0])
        self.assertEqual(check_LGR_error(lgr1)[0][0],
                         elma.error.ERR_LGR_INVALID_PALETTE)
        lgr1.palette = LGR_DEFAULT_PALETTE
        # ERR_LGR_MISSING_MANDATORY_FILE
        tempLGRIm = lgr1.images.pop(0)
        self.assertEqual(check_LGR_error(lgr1)[0][0],
                         elma.error.ERR_LGR_MISSING_MANDATORY_FILE)
        # ERR_DUPLICATE_NAME
        lgr1.images.extend([tempLGRIm, tempLGRIm])
        self.assertEqual(check_LGR_error(lgr1)[0][0],
                         elma.error.ERR_DUPLICATE_NAME)
        lgr1.images.insert(0, tempLGRIm)  # reset to normal
        lgr1.images.pop()
        lgr1.images.pop()
        # ERR_TOO_MANY_GRASS
        for i in range(30, 80):  # skip the already-present qups and qdowns
            # keep height of grass to avoid warning
            imgt = Image.new("P", (1, 41), 0)
            imgt.putpalette(lgr1.palette)
            lgr1.images.append(LGR_Image(
                "qUp_%s" % i,
                imgt,
                LGR_Image.PICTURE,
                999,
                LGR_Image.CLIPPING_G,
                LGR_Image.TRANSPARENCY_PAL_ZERO))
        for i in range(30, 80):
            imgt = Image.new("P", (1, 41), 0)
            imgt.putpalette(lgr1.palette)
            lgr1.images.append(LGR_Image(
                "qDowN_%s" % i,
                imgt,
                LGR_Image.PICTURE,
                999,
                LGR_Image.CLIPPING_G,
                LGR_Image.TRANSPARENCY_PAL_ZERO))
        self.assertEqual(check_LGR_error(lgr1)[0][0],
                         elma.error.ERR_TOO_MANY_GRASS)
        del lgr1.images[-100:]
        # Just double-check we are back to the normal list
        self.assertEqual(len(lgr1.images), len(lgr2.images))
        # ERR_TOO_MANY_PICTURES
        for i in range(1000):
            imgt = Image.new("P", (1, 1), 0)
            imgt.putpalette(lgr1.palette)
            lgr1.images.append(LGR_Image(
                "pic%s" % i,
                imgt,
                LGR_Image.PICTURE,
                999,
                LGR_Image.CLIPPING_G,
                LGR_Image.TRANSPARENCY_PAL_ZERO))
        self.assertEqual(check_LGR_error(lgr1)[0][0],
                         elma.error.ERR_TOO_MANY_PICTURES)
        del lgr1.images[-1000:]
        self.assertEqual(len(lgr1.images), len(lgr2.images))
        # ERR_TOO_MANY_TEXTURES
        for i in range(100):
            imgt = Image.new("P", (1, 1), 0)
            imgt.putpalette(lgr1.palette)
            lgr1.images.append(LGR_Image(
                "pic%s" % i,
                imgt,
                LGR_Image.TEXTURE,
                999,
                LGR_Image.CLIPPING_G,
                LGR_Image.TRANSPARENCY_PAL_ZERO))
        self.assertEqual(check_LGR_error(lgr1)[0][0],
                         elma.error.ERR_TOO_MANY_TEXTURES)
        del lgr1.images[-100:]
        self.assertEqual(len(lgr1.images), len(lgr2.images))
        # ERR_NOT_ENOUGH_TEXTURES
        tempimages = lgr1.images[:]
        del lgr1.images[lgr1.find_LGR_Image("brick")]
        del lgr1.images[lgr1.find_LGR_Image("ground")]
        del lgr1.images[lgr1.find_LGR_Image("sky")]
        del lgr1.images[lgr1.find_LGR_Image("stone1")]
        del lgr1.images[lgr1.find_LGR_Image("stone2")]
        del lgr1.images[lgr1.find_LGR_Image("stone3")]
        self.assertEqual(check_LGR_error(lgr1)[0][0],
                         elma.error.ERR_NOT_ENOUGH_TEXTURES)
        lgr1.images = tempimages[:]
        self.assertEqual(len(lgr1.images), len(lgr2.images))
        # ERR_TOO_MANY_MASKS
        for i in range(200):
            imgt = Image.new("P", (1, 1), 0)
            imgt.putpalette(lgr1.palette)
            lgr1.images.append(LGR_Image(
                "pic%s" % i,
                imgt,
                LGR_Image.MASK,
                999,
                LGR_Image.CLIPPING_G,
                LGR_Image.TRANSPARENCY_PAL_ZERO))
        self.assertEqual(check_LGR_error(lgr1)[0][0],
                         elma.error.ERR_TOO_MANY_MASKS)
        del lgr1.images[-200:]
        self.assertEqual(len(lgr1.images), len(lgr2.images))
        # WARN_UNUSED_QFOOD
        imgt = Image.new("P", (40, 40), 0)
        imgt.putpalette(lgr1.palette)
        lgr1.images.append(LGR_Image("qfOod4", imgt))
        self.assertEqual(check_LGR_error(lgr1)[0][0],
                         elma.error.WARN_UNUSED_QFOOD)
        # ERR_NAME_TOO_LONG
        lgr1.images[-1].name = "nameTOOlong"
        self.assertEqual(check_LGR_error(lgr1)[0][0],
                         elma.error.ERR_NAME_TOO_LONG)
        # ERR_NAME_MISSING
        lgr1.images[-1].name = ""
        self.assertEqual(check_LGR_error(lgr1)[0][0],
                         elma.error.ERR_NAME_MISSING)
        # ERR_PADDING_INVALID
        lgr1.images[-1].name = "x"
        lgr1.images[-1].padding = [1, 2, 3, 4, 5, 6, 7, 8]
        self.assertEqual(check_LGR_error(lgr1)[0][0],
                         elma.error.ERR_PADDING_INVALID)
        lgr1.images[-1].padding = [1, 2, 3, 4, 5, 600, 7]
        self.assertEqual(check_LGR_error(lgr1)[0][0],
                         elma.error.ERR_PADDING_INVALID)
        lgr1.images[-1].padding = [1, 2, 3, 4, 5, "error", 7]
        self.assertEqual(check_LGR_error(lgr1)[0][0],
                         elma.error.ERR_PADDING_INVALID)
        lgr1.images[-1].padding = [1, 2, 3, 4, 5, 6, 7]
        # WARN_GRASS_HEIGHT_TOO_SMALL
        imgt = Image.new("P", (41, 40), 0)
        imgt.putpalette(lgr1.palette)
        lgr1.images[-1].name = "qUp_Xx"
        lgr1.images[-1].img = imgt
        self.assertEqual(check_LGR_error(lgr1)[0][0],
                         elma.error.WARN_GRASS_HEIGHT_TOO_SMALL)
        # ERR_OBJ_WIDTH_INVALID
        lgr1.images[-1].name = "qFOOd3"
        self.assertEqual(check_LGR_error(lgr1)[0][0],
                         elma.error.ERR_OBJ_WIDTH_INVALID)
        # WARN_OBJ_HEIGHT_INVALID
        imgt = Image.new("P", (40, 1), 0)
        imgt.putpalette(lgr1.palette)
        lgr1.images[-1].img = imgt
        self.assertEqual(check_LGR_error(lgr1)[0][0],
                         elma.error.WARN_OBJ_HEIGHT_INVALID)
        # ERR_OBJ_TOO_WIDE
        imgt = Image.new("P", (40040, 40), 0)
        imgt.putpalette(lgr1.palette)
        lgr1.images[-1].img = imgt
        self.assertEqual(check_LGR_error(lgr1)[0][0],
                         elma.error.ERR_OBJ_TOO_WIDE)
        # ERR_IMAGE_TYPE_INVALID
        lgr1.images[-1].name = "x"
        imgt = Image.new("P", (1, 1), 0)
        imgt.putpalette(lgr1.palette)
        lgr1.images[-1].img = imgt
        lgr1.images[-1].image_type = 30
        self.assertEqual(check_LGR_error(lgr1)[0][0],
                         elma.error.ERR_IMAGE_TYPE_INVALID)
        lgr1.images[-1].image_type = LGR_Image.PICTURE
        # ERR_PIC_TOO_WIDE
        imgt = Image.new("P", (6001, 1), 0)
        imgt.putpalette(lgr1.palette)
        lgr1.images[-1].img = imgt
        self.assertEqual(check_LGR_error(lgr1)[0][0],
                         elma.error.ERR_PIC_TOO_WIDE)
        # ERR_PIC_TOO_MANY_PIXELS
        imgt = Image.new("P", (800, 780), 0)
        imgt.putpalette(lgr1.palette)
        lgr1.images[-1].img = imgt
        self.assertEqual(check_LGR_error(lgr1)[0][0],
                         elma.error.ERR_PIC_TOO_MANY_PIXELS)
        # ERR_DISTANCE_INVALID
        imgt = Image.new("P", (1, 1), 0)
        imgt.putpalette(lgr1.palette)
        lgr1.images[-1].img = imgt
        lgr1.images[-1].default_distance = 0
        self.assertEqual(check_LGR_error(lgr1)[0][0],
                         elma.error.ERR_DISTANCE_INVALID)
        lgr1.images[-1].default_distance = 1000
        self.assertEqual(check_LGR_error(lgr1)[0][0],
                         elma.error.ERR_DISTANCE_INVALID)
        lgr1.images[-1].image_type = LGR_Image.MASK
        self.assertEqual(check_LGR_error(lgr1), [])
        lgr1.images[-1].default_distance = 500
        # ERR_CLIPPING_INVALID
        lgr1.images[-1].default_clipping = 10
        self.assertEqual(check_LGR_error(lgr1), [])
        lgr1.images[-1].image_type = LGR_Image.TEXTURE
        self.assertEqual(check_LGR_error(lgr1)[0][0],
                         elma.error.ERR_CLIPPING_INVALID)
        lgr1.images[-1].default_clipping = -1
        self.assertEqual(check_LGR_error(lgr1)[0][0],
                         elma.error.ERR_CLIPPING_INVALID)
        LGR_Image.default_clipping = LGR_Image.CLIPPING_G
        lgr1.images[-1].default_clipping = LGR_Image.default_clipping
        # ERR_TRANSPARENCY_INVALID
        lgr1.images[-1].transparency = 100
        self.assertEqual(check_LGR_error(lgr1)[0][0],
                         elma.error.ERR_TRANSPARENCY_INVALID)
        lgr1.images[-1].transparency = -1
        self.assertEqual(check_LGR_error(lgr1)[0][0],
                         elma.error.ERR_TRANSPARENCY_INVALID)
        lgr1.images[-1].transparency = LGR_Image.TRANSPARENCY_PAL_ZERO
        # ERR_FILE_TOO_LARGE
        sizing = 2400
        # palette numbers 193-255 take up 2 bytes in .pcx format instead of
        # one. 2400*2400*2 > 10,000,000
        imgt = Image.new("P", (sizing, sizing), 200)
        imgt.putpalette(lgr1.palette)
        draw = ImageDraw.Draw(imgt)
        # hatch the image because .pcx format uses run-length-encoding of same
        # value in horizontal sequence
        for i in range(0, sizing, 2):
            draw.line([i, 0, sizing-1, sizing-1-i], fill=201, width=1)
            draw.line([0, i, sizing-1-i, sizing-1], fill=201, width=1)
        del draw
        imgt.save("tests/files/result/err_file_too_large.pcx", "pcx")
        lgr1.images[-1].img = imgt
        self.assertEqual(check_LGR_error(lgr1)[0][0],
                         elma.error.ERR_FILE_TOO_LARGE)
        del lgr1.images[-1]
        # ERR_SMALL_IMAGE_TOO_LARGE
        img_temp = lgr1.images[4].img
        imgt = Image.new("P", (256, 255), 0)
        imgt.putpalette(lgr1.palette)
        lgr1.images[4].img = imgt
        self.assertEqual(check_LGR_error(lgr1)[0][0],
                         elma.error.ERR_SMALL_IMAGE_TOO_LARGE)
        imgt = Image.new("P", (255, 256), 0)
        imgt.putpalette(lgr1.palette)
        lgr1.images[4].img = imgt
        self.assertEqual(check_LGR_error(lgr1)[0][0],
                         elma.error.ERR_SMALL_IMAGE_TOO_LARGE)
        lgr1.images[4].img = img_temp
        # WARN_PALETTE_MISMATCH
        editted_palette = LGR_DEFAULT_PALETTE[:]
        editted_palette[0] = 100
        lgr1.images[4].put_palette(editted_palette)
        self.assertEqual(check_LGR_error(lgr1)[0][0],
                         elma.error.WARN_PALETTE_MISMATCH)
        editted_palette[0] = 0
        lgr1.images[4].put_palette(editted_palette)
        # ERR_IMAGE_INVALID_PALETTE
        imgt = Image.new("RGB", (1, 1), 0)
        lgr1.images.append(LGR_Image(
            "x",
            imgt,
            LGR_Image.MASK,
            999,
            LGR_Image.CLIPPING_G,
            LGR_Image.TRANSPARENCY_PAL_ZERO))
        self.assertEqual(check_LGR_error(lgr1)[0][0],
                         elma.error.ERR_IMAGE_INVALID_PALETTE)
        del lgr1.images[-1]
        # WARN_QCOLORS_WRONG_SIZE
        index = lgr1.find_LGR_Image("qCOlorS")
        img_temp = lgr1.images[index].img
        imgt = Image.new("P", (67, 109), 0)
        imgt.putpalette(lgr1.palette)
        lgr1.images[index].img = imgt
        self.assertEqual(check_LGR_error(lgr1)[0][0],
                         elma.error.WARN_QCOLORS_WRONG_SIZE)
        imgt = Image.new("P", (66, 108), 0)
        imgt.putpalette(lgr1.palette)
        lgr1.images[index].img = imgt
        self.assertEqual(check_LGR_error(lgr1)[0][0],
                         elma.error.WARN_QCOLORS_WRONG_SIZE)
        lgr1.images[index].img = img_temp
        # WARN_QBIKE_TOO_SMALL
        index = lgr1.find_LGR_Image("q2BIKE")
        img_temp = lgr1.images[index].img
        imgt = Image.new("P", (353, 298), 0)
        imgt.putpalette(lgr1.palette)
        lgr1.images[index].img = imgt
        self.assertEqual(check_LGR_error(lgr1)[0][0],
                         elma.error.WARN_QBIKE_TOO_SMALL)
        imgt = Image.new("P", (354, 297), 0)
        imgt.putpalette(lgr1.palette)
        lgr1.images[index].img = imgt
        self.assertEqual(check_LGR_error(lgr1)[0][0],
                         elma.error.WARN_QBIKE_TOO_SMALL)
        # ERR_IMG_MISSING
        lgr1.images[index].img = None
        self.assertEqual(check_LGR_error(lgr1)[0][0],
                         elma.error.ERR_IMG_MISSING)
        lgr1.images[index].img = img_temp
