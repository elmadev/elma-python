from elma.lgr import LGR
from elma.lgr import LGR_Image
from elma.lgr import pack_LGR
from elma.lgr import unpack_LGR
import elma.error
from elma.error import check_LGR_error
from elma.constants import LGR_DEFAULT_PALETTE
import unittest
from PIL import Image
from PIL import ImageDraw
import os
import shutil


class TestLGR(unittest.TestCase):

    def setUp(self):
        os.makedirs('tests/files/result', exist_ok=True)

    def tearDown(self):
        try:
            shutil.rmtree("tests/files/result")
        except FileNotFoundError:
            pass

    def test_get_palette(self):
        with Image.open('tests/files/barrel.pcx') as image:
            barrel = LGR_Image('barrel', img=image)
            self.assertEqual(barrel.get_palette(), LGR_DEFAULT_PALETTE)

    def test_is_methods(self):
        lgrimg = LGR_Image('barrel')
        self.assertEqual(lgrimg.is_in_pictures_lst(), True)
        self.assertEqual(lgrimg.is_qup_qdown(), False)
        self.assertEqual(lgrimg.is_food(), False)
        self.assertEqual(lgrimg.is_special(), False)
        lgrimg = LGR_Image('q1body')
        self.assertEqual(lgrimg.is_in_pictures_lst(), False)
        self.assertEqual(lgrimg.is_qup_qdown(), False)
        self.assertEqual(lgrimg.is_food(), False)
        self.assertEqual(lgrimg.is_special(), True)
        lgrimg = LGR_Image('Q1BODY')
        self.assertEqual(lgrimg.is_in_pictures_lst(), False)
        self.assertEqual(lgrimg.is_qup_qdown(), False)
        self.assertEqual(lgrimg.is_food(), False)
        self.assertEqual(lgrimg.is_special(), True)
        lgrimg = LGR_Image('qFoOd5')
        self.assertEqual(lgrimg.is_in_pictures_lst(), True)
        self.assertEqual(lgrimg.is_qup_qdown(), False)
        self.assertEqual(lgrimg.is_food(), True)
        self.assertEqual(lgrimg.is_special(), True)
        lgrimg = LGR_Image('qUp_xS')
        self.assertEqual(lgrimg.is_in_pictures_lst(), True)
        self.assertEqual(lgrimg.is_qup_qdown(), True)
        self.assertEqual(lgrimg.is_food(), False)
        self.assertEqual(lgrimg.is_special(), True)

    def test_is_valid_palette_image(self):
        with Image.open('tests/files/barrel.pcx') as f:
            lgrimg = LGR_Image('barrel', img=f)
            self.assertEqual(lgrimg.is_valid_palette_image(), True)
        with Image.open('tests/files/barrel.bmp') as f:
            lgrimg = LGR_Image('barrel', img=f)
            self.assertEqual(lgrimg.is_valid_palette_image(), True)
        with Image.open('tests/files/barrelgrayscale.bmp') as f:
            lgrimg = LGR_Image('barrel', img=f)
            self.assertEqual(lgrimg.is_valid_palette_image(), False)
        with Image.open('tests/files/barrelrgb.png') as f:
            lgrimg = LGR_Image('barrel', img=f)
            self.assertEqual(lgrimg.is_valid_palette_image(), False)
        with Image.open('tests/files/barrel_partial_palette.pcx') as f:
            lgrimg = LGR_Image('barrel', img=f)
            self.assertEqual(lgrimg.is_valid_palette_image(), True)

    def test_convert_palette_image(self):
        with Image.open('tests/files/barrelrgb.png') as f:
            lgrimg = LGR_Image('barrel', img=f)
            lgrimg.convert_palette_image(
                palette_info=LGR_DEFAULT_PALETTE,
                dither=False)
            lgrimg.save_PCX("tests/files/result/barrelrgb2pal.pcx")
            with Image.open('tests/files/barrel.pcx') as g:
                self.assertEqual(lgrimg.img.mode, g.mode)
                self.assertEqual(lgrimg.img.size, g.size)
                self.assertEqual(lgrimg.img.getpalette(), g.getpalette())
                self.assertEqual(lgrimg.img.tobytes(), g.tobytes())
        with Image.open('tests/files/woman.png') as f:
            lgrimg = LGR_Image('woman', img=f)
            lgrimg.convert_palette_image(
                LGR_DEFAULT_PALETTE, True)
            lgrimg.save_PCX('tests/files/result/woman.pcx')
            self.assertEqual(lgrimg.img.getpalette(), LGR_DEFAULT_PALETTE)
        with Image.open('tests/files/barrel_partial_palette.pcx') as f:
            lgrimg = LGR_Image('barrel', img=f)
            lgrimg.convert_palette_image(
                palette_info=LGR_DEFAULT_PALETTE, dither=False)
            lgrimg.save_PCX(
                "tests/files/result/barrel_partial_to_full_palette.pcx")
            with Image.open('tests/files/barrel.pcx') as g:
                self.assertEqual(lgrimg.img.mode, g.mode)
                self.assertEqual(lgrimg.img.size, g.size)
                self.assertEqual(lgrimg.img.getpalette(), g.getpalette())
                self.assertEqual(lgrimg.img.tobytes(), g.tobytes())

    def test_packing_and_unpacking(self):
        lgr1 = unpack_LGR('tests/files/default.lgr')
        with open('tests/files/result/default.lgr', 'wb') as f:
            f.write(pack_LGR(lgr1))
        # not comparing binaries here because the script changes pcx header &
        # compresses a bit better than original .pcx files
        lgr2 = unpack_LGR('tests/files/result/default.lgr')
        self.assertEqual(lgr1.palette, lgr2.palette)
        for k in range(len(lgr1.images)):
            self.assertEqual(lgr1.images[k], lgr2.images[k])

    def test_find_LGR_Image(self):
        lgr = LGR()
        lgr.images.append(LGR_Image('aAa'))
        lgr.images.append(LGR_Image('bBb'))
        lgr.images.append(LGR_Image('cCc'))
        lgr.images.append(LGR_Image('dDd'))
        lgr.images.append(LGR_Image('eEe'))
        index = lgr.find_LGR_Image("DdD")
        self.assertEqual(index, 3)
        self.assertRaises(ValueError,
                          lambda: lgr.find_LGR_Image("does not exist"))


class TestLGRErrors(unittest.TestCase):

    def setUp(self):
        self.lgr = unpack_LGR('tests/files/default.lgr')
        os.makedirs('tests/files/result', exist_ok=True)

    def tearDown(self):
        try:
            shutil.rmtree("tests/files/result")
        except FileNotFoundError:
            pass

    def test_error_no_errors(self):
        self.assertEqual(check_LGR_error(self.lgr), [])

    def test_error_invalid_palette(self):
        self.lgr.palette[0] = 300
        self.assertEqual(check_LGR_error(self.lgr)[0][0],
                         elma.error.ERR_LGR_INVALID_PALETTE)
        self.lgr.palette[0] = -10
        self.assertEqual(check_LGR_error(self.lgr)[0][0],
                         elma.error.ERR_LGR_INVALID_PALETTE)
        self.lgr.palette[0] = 0
        self.lgr.palette.append([0])
        self.assertEqual(check_LGR_error(self.lgr)[0][0],
                         elma.error.ERR_LGR_INVALID_PALETTE)

    def test_error_missing_mandatory_file(self):
        self.lgr.images.pop(0)
        self.assertEqual(check_LGR_error(self.lgr)[0][0],
                         elma.error.ERR_LGR_MISSING_MANDATORY_FILE)

    def test_error_duplicate_name(self):
        self.lgr.images.append(self.lgr.images[-1])
        self.assertEqual(check_LGR_error(self.lgr)[0][0],
                         elma.error.ERR_DUPLICATE_NAME)

    def test_error_too_many_grass(self):
        for i in range(30, 80):  # skip the already-present qups and qdowns
            # keep height of grass to avoid warning
            imgt = Image.new('P', (1, 41), 0)
            imgt.putpalette(self.lgr.palette)
            self.lgr.images.append(LGR_Image(
                'qUp_%s' % i,
                imgt,
                LGR_Image.PICTURE,
                999,
                LGR_Image.CLIPPING_G,
                LGR_Image.TRANSPARENCY_PAL_ZERO))
        for i in range(30, 80):
            imgt = Image.new('P', (1, 41), 0)
            imgt.putpalette(self.lgr.palette)
            self.lgr.images.append(LGR_Image(
                'qDowN_%s' % i,
                imgt,
                LGR_Image.PICTURE,
                999,
                LGR_Image.CLIPPING_G,
                LGR_Image.TRANSPARENCY_PAL_ZERO))
        self.assertEqual(check_LGR_error(self.lgr)[0][0],
                         elma.error.ERR_TOO_MANY_GRASS)

    def test_error_too_many_pictures(self):
        for i in range(1000):
            imgt = Image.new('P', (1, 1), 0)
            imgt.putpalette(self.lgr.palette)
            self.lgr.images.append(LGR_Image(
                'pic%s' % i,
                imgt,
                LGR_Image.PICTURE,
                999,
                LGR_Image.CLIPPING_G,
                LGR_Image.TRANSPARENCY_PAL_ZERO))
        self.assertEqual(check_LGR_error(self.lgr)[0][0],
                         elma.error.ERR_TOO_MANY_PICTURES)

    def test_error_too_many_textures(self):
        for i in range(100):
            imgt = Image.new('P', (1, 1), 0)
            imgt.putpalette(self.lgr.palette)
            self.lgr.images.append(LGR_Image(
                'pic%s' % i,
                imgt,
                LGR_Image.TEXTURE,
                999,
                LGR_Image.CLIPPING_G,
                LGR_Image.TRANSPARENCY_PAL_ZERO))
        self.assertEqual(check_LGR_error(self.lgr)[0][0],
                         elma.error.ERR_TOO_MANY_TEXTURES)

    def test_error_not_enough_textures(self):
        del self.lgr.images[self.lgr.find_LGR_Image("brick")]
        del self.lgr.images[self.lgr.find_LGR_Image("ground")]
        del self.lgr.images[self.lgr.find_LGR_Image("sky")]
        del self.lgr.images[self.lgr.find_LGR_Image("stone1")]
        del self.lgr.images[self.lgr.find_LGR_Image("stone2")]
        del self.lgr.images[self.lgr.find_LGR_Image("stone3")]
        self.assertEqual(check_LGR_error(self.lgr)[0][0],
                         elma.error.ERR_NOT_ENOUGH_TEXTURES)

    def test_error_too_many_masks(self):
        for i in range(200):
            imgt = Image.new('P', (1, 1), 0)
            imgt.putpalette(self.lgr.palette)
            self.lgr.images.append(LGR_Image(
                'pic%s' % i,
                imgt,
                LGR_Image.MASK,
                999,
                LGR_Image.CLIPPING_G,
                LGR_Image.TRANSPARENCY_PAL_ZERO))
        self.assertEqual(check_LGR_error(self.lgr)[0][0],
                         elma.error.ERR_TOO_MANY_MASKS)

    def test_warning_unused_qfood(self):
        imgt = Image.new('P', (40, 40), 0)
        imgt.putpalette(self.lgr.palette)
        self.lgr.images.append(LGR_Image('qfOod4', imgt))
        self.assertEqual(check_LGR_error(self.lgr)[0][0],
                         elma.error.WARN_UNUSED_QFOOD)

    def test_error_name_too_long(self):
        self.lgr.images[-1].name = 'nameTOOlong'
        self.assertEqual(check_LGR_error(self.lgr)[0][0],
                         elma.error.ERR_NAME_TOO_LONG)

    def test_error_name_missing(self):
        self.lgr.images[-1].name = ''
        self.assertEqual(check_LGR_error(self.lgr)[0][0],
                         elma.error.ERR_NAME_MISSING)

    def test_error_padding_invalid(self):
        self.lgr.images[-1].name = "x"
        self.lgr.images[-1].padding = [1, 2, 3, 4, 5, 6, 7, 8]
        self.assertEqual(check_LGR_error(self.lgr)[0][0],
                         elma.error.ERR_PADDING_INVALID)
        self.lgr.images[-1].padding = [1, 2, 3, 4, 5, 600, 7]
        self.assertEqual(check_LGR_error(self.lgr)[0][0],
                         elma.error.ERR_PADDING_INVALID)
        self.lgr.images[-1].padding = [1, 2, 3, 4, 5, 'error', 7]
        self.assertEqual(check_LGR_error(self.lgr)[0][0],
                         elma.error.ERR_PADDING_INVALID)

    def test_warning_grass_height_too_small(self):
        imgt = Image.new('P', (41, 40), 0)
        imgt.putpalette(self.lgr.palette)
        self.lgr.images[-1].name = "qUp_Xx"
        self.lgr.images[-1].img = imgt
        self.assertEqual(check_LGR_error(self.lgr)[0][0],
                         elma.error.WARN_GRASS_HEIGHT_TOO_SMALL)

    def test_error_obj_width_invalid(self):
        imgt = Image.new("P", (41, 40), 0)
        imgt.putpalette(self.lgr.palette)
        self.lgr.images[-1].name = "qFOOd3"
        self.lgr.images[-1].img = imgt
        self.assertEqual(check_LGR_error(self.lgr)[0][0],
                         elma.error.ERR_OBJ_WIDTH_INVALID)

    def test_error_obj_height_invalid(self):
        imgt = Image.new('P', (40, 1), 0)
        imgt.putpalette(self.lgr.palette)
        self.lgr.images[-1].name = "qFOOd3"
        self.lgr.images[-1].img = imgt
        self.assertEqual(check_LGR_error(self.lgr)[0][0],
                         elma.error.WARN_OBJ_HEIGHT_INVALID)

    def test_error_obj_too_wide(self):
        imgt = Image.new('P', (40040, 40), 0)
        imgt.putpalette(self.lgr.palette)
        self.lgr.images[-1].name = "qFOOd3"
        self.lgr.images[-1].img = imgt
        self.assertEqual(check_LGR_error(self.lgr)[0][0],
                         elma.error.ERR_OBJ_TOO_WIDE)

    def test_error_image_type_invalid(self):
        self.lgr.images[-1].name = 'x'
        imgt = Image.new('P', (1, 1), 0)
        imgt.putpalette(self.lgr.palette)
        self.lgr.images[-1].img = imgt
        self.lgr.images[-1].image_type = 30
        self.assertEqual(check_LGR_error(self.lgr)[0][0],
                         elma.error.ERR_IMAGE_TYPE_INVALID)

    def test_error_pic_too_wide(self):
        imgt = Image.new('P', (6001, 1), 0)
        imgt.putpalette(self.lgr.palette)
        self.lgr.images[-1].img = imgt
        self.assertEqual(check_LGR_error(self.lgr)[0][0],
                         elma.error.ERR_PIC_TOO_WIDE)

    def test_error_pic_too_many_pixels(self):
        imgt = Image.new('P', (800, 780), 0)
        imgt.putpalette(self.lgr.palette)
        self.lgr.images[-1].img = imgt
        self.assertEqual(check_LGR_error(self.lgr)[0][0],
                         elma.error.ERR_PIC_TOO_MANY_PIXELS)

    def test_error_distance_invalid(self):
        imgt = Image.new('P', (1, 1), 0)
        imgt.putpalette(self.lgr.palette)
        self.lgr.images[-1].img = imgt
        self.lgr.images[-1].default_distance = 0
        self.assertEqual(check_LGR_error(self.lgr)[0][0],
                         elma.error.ERR_DISTANCE_INVALID)
        self.lgr.images[-1].default_distance = 1000
        self.assertEqual(check_LGR_error(self.lgr)[0][0],
                         elma.error.ERR_DISTANCE_INVALID)
        self.lgr.images[-1].image_type = LGR_Image.MASK
        self.assertEqual(check_LGR_error(self.lgr), [])

    def test_error_clipping_invalid(self):
        self.lgr.images[-1].image_type = LGR_Image.MASK
        self.lgr.images[-1].default_clipping = 10
        self.assertEqual(check_LGR_error(self.lgr), [])
        self.lgr.images[-1].image_type = LGR_Image.TEXTURE
        self.assertEqual(check_LGR_error(self.lgr)[0][0],
                         elma.error.ERR_CLIPPING_INVALID)
        self.lgr.images[-1].default_clipping = -1
        self.assertEqual(check_LGR_error(self.lgr)[0][0],
                         elma.error.ERR_CLIPPING_INVALID)

    def test_error_transparency_invalid(self):
        self.lgr.images[-1].transparency = 100
        self.assertEqual(check_LGR_error(self.lgr)[0][0],
                         elma.error.ERR_TRANSPARENCY_INVALID)
        self.lgr.images[-1].transparency = -1
        self.assertEqual(check_LGR_error(self.lgr)[0][0],
                         elma.error.ERR_TRANSPARENCY_INVALID)

    def test_error_file_too_large(self):
        sizing = 2400
        # palette numbers 193-255 take up 2 bytes in .pcx format instead of
        # one. 2400*2400*2 > 10,000,000
        imgt = Image.new('P', (sizing, sizing), 200)
        imgt.putpalette(self.lgr.palette)
        draw = ImageDraw.Draw(imgt)
        # hatch the image because .pcx format uses run-length-encoding of same
        # value in horizontal sequence
        for i in range(0, sizing, 2):
            draw.line([i, 0, sizing-1, sizing-1-i], fill=201, width=1)
            draw.line([0, i, sizing-1-i, sizing-1], fill=201, width=1)
        del draw
        imgt.save('tests/files/result/err_file_too_large.pcx', 'pcx')
        self.lgr.images[-1].img = imgt
        self.lgr.images[-1].image_type = LGR_Image.TEXTURE
        self.assertEqual(check_LGR_error(self.lgr)[0][0],
                         elma.error.ERR_FILE_TOO_LARGE)

    def test_error_small_image_too_large(self):
        imgt = Image.new('P', (256, 255), 0)
        imgt.putpalette(self.lgr.palette)
        self.lgr.images[4].img = imgt
        self.assertEqual(check_LGR_error(self.lgr)[0][0],
                         elma.error.ERR_SMALL_IMAGE_TOO_LARGE)
        imgt = Image.new('P', (255, 256), 0)
        imgt.putpalette(self.lgr.palette)
        self.lgr.images[4].img = imgt
        self.assertEqual(check_LGR_error(self.lgr)[0][0],
                         elma.error.ERR_SMALL_IMAGE_TOO_LARGE)

    def test_warning_palette_mismatch(self):
        edited_palette = LGR_DEFAULT_PALETTE[:]
        edited_palette[0] = 100
        self.lgr.images[4].put_palette(edited_palette)
        self.assertEqual(check_LGR_error(self.lgr)[0][0],
                         elma.error.WARN_PALETTE_MISMATCH)

    def test_error_image_invalid_palette(self):
        imgt = Image.new('RGB', (1, 1), 0)
        self.lgr.images.append(LGR_Image(
            'x',
            imgt,
            LGR_Image.MASK,
            999,
            LGR_Image.CLIPPING_G,
            LGR_Image.TRANSPARENCY_PAL_ZERO))
        self.assertEqual(check_LGR_error(self.lgr)[0][0],
                         elma.error.ERR_IMAGE_INVALID_PALETTE)

    def test_warning_qcolors_wrong_size(self):
        index = self.lgr.find_LGR_Image('qCOlorS')
        imgt = Image.new('P', (67, 109), 0)
        imgt.putpalette(self.lgr.palette)
        self.lgr.images[index].img = imgt
        self.assertEqual(check_LGR_error(self.lgr)[0][0],
                         elma.error.WARN_QCOLORS_WRONG_SIZE)
        imgt = Image.new("P", (66, 108), 0)
        imgt.putpalette(self.lgr.palette)
        self.lgr.images[index].img = imgt
        self.assertEqual(check_LGR_error(self.lgr)[0][0],
                         elma.error.WARN_QCOLORS_WRONG_SIZE)

    def test_warning_qbike_too_small(self):
        index = self.lgr.find_LGR_Image("q2BIKE")
        imgt = Image.new("P", (353, 298), 0)
        imgt.putpalette(self.lgr.palette)
        self.lgr.images[index].img = imgt
        self.assertEqual(check_LGR_error(self.lgr)[0][0],
                         elma.error.WARN_QBIKE_TOO_SMALL)
        imgt = Image.new("P", (354, 297), 0)
        imgt.putpalette(self.lgr.palette)
        self.lgr.images[index].img = imgt
        self.assertEqual(check_LGR_error(self.lgr)[0][0],
                         elma.error.WARN_QBIKE_TOO_SMALL)

    def test_error_img_missing(self):
        self.lgr.images[0].img = None
        self.assertEqual(check_LGR_error(self.lgr)[0][0],
                         elma.error.ERR_IMG_MISSING)
