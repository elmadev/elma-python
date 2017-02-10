import sys
import os
sys.path.insert(0, os.path.abspath('..'))

from elma.lgr import unpack_LGR
from elma.lgr import pack_LGR
from elma.lgr import LGR_Image
from elma.lgr import LGR
from elma.error import check_LGR_error
from elma.constants import LGR_DEFAULT_PALETTE
import unittest
from PIL import Image

class TestLGR(unittest.TestCase):
    def test_LGR_Image(self):
        #Test get_palette()
        with Image.open('files/barrel.pcx') as f:
            lgrimg=LGR_Image('barrel',f)
            self.assertEqual(lgrimg.get_palette(),LGR_DEFAULT_PALETTE)
        
        #Test is_in_pictures_lst()
        lgrimg=LGR_Image('barrel')
        self.assertEqual(lgrimg.is_in_pictures_lst(),True)
        lgrimg.name="q1body"
        self.assertEqual(lgrimg.is_in_pictures_lst(),False)
        lgrimg.name="Q1BODY"
        self.assertEqual(lgrimg.is_in_pictures_lst(),False)
        
        #Test is_valid_palette_image()
        with Image.open('files/barrel.pcx') as f:
            lgrimg=LGR_Image('barrel',f)
            self.assertEqual(lgrimg.is_valid_palette_image(),True)
        with Image.open('files/barrel.bmp') as f:
            lgrimg=LGR_Image('barrel',f)
            self.assertEqual(lgrimg.is_valid_palette_image(),True)
        with Image.open('files/barrelgrayscale.bmp') as f:
            lgrimg=LGR_Image('barrel',f)
            self.assertEqual(lgrimg.is_valid_palette_image(),False)
        with Image.open('files/barrelrgb.png') as f:
            lgrimg=LGR_Image('barrel',f)
            self.assertEqual(lgrimg.is_valid_palette_image(),False)
        with Image.open('files/barrel_partial_palette.pcx') as f:
            lgrimg=LGR_Image('barrel',f)
            self.assertEqual(lgrimg.is_valid_palette_image(),True)

        #Test convert_palette_image()
        with Image.open('files/barrelrgb.png') as f:
            lgrimg=LGR_Image('barrel',f)
            lgrimg.img=lgrimg.convert_palette_image(palette_info=LGR_DEFAULT_PALETTE,dither=False)
            os.makedirs(os.path.dirname("files/result/barrelrgb2pal.pcx"), exist_ok=True)
            lgrimg.save_PCX("files/result/barrelrgb2pal.pcx")
            with Image.open('files/barrel.pcx') as g:
                self.assertEqual(lgrimg.img.mode,g.mode)
                self.assertEqual(lgrimg.img.size,g.size)
                self.assertEqual(lgrimg.img.getpalette(),g.getpalette())
                self.assertEqual(lgrimg.img.tobytes(),g.tobytes())
        with Image.open('files/woman.png') as f:
            lgrimg=LGR_Image('woman',f)
            lgrimg.img=lgrimg.convert_palette_image(LGR_DEFAULT_PALETTE,True)
            lgrimg.save_PCX('files/result/woman.pcx')
            self.assertEqual(lgrimg.img.getpalette(),LGR_DEFAULT_PALETTE)
        with Image.open('files/barrel_partial_palette.pcx') as f:
            lgrimg=LGR_Image('barrel',f)
            lgrimg.img=lgrimg.convert_palette_image(palette_info=LGR_DEFAULT_PALETTE,dither=False)
            lgrimg.save_PCX("files/result/barrel_partial_to_full_palette.pcx")
            with Image.open('files/barrel.pcx') as g:
                self.assertEqual(lgrimg.img.mode,g.mode)
                self.assertEqual(lgrimg.img.size,g.size)
                self.assertEqual(lgrimg.img.getpalette(),g.getpalette())
                self.assertEqual(lgrimg.img.tobytes(),g.tobytes())
        
        #Test packing and unpacking
        lgr1=unpack_LGR('files/default.lgr')
        with open('files/result/default.lgr','wb') as f:
            f.write(pack_LGR(lgr1))
        lgr2=unpack_LGR('files/result/default.lgr') #not comparing binaries here because my script changes pcx header & compresses a bit better than original .pcx files
        self.assertEqual(lgr1.palette,lgr2.palette)
        for k in range(len(lgr1.images)):
            self.assertEqual(lgr1.images[k],lgr2.images[k])
        
        #Test error-checking
        self.assertEqual(check_LGR_error(lgr1),[])

unittest.main()