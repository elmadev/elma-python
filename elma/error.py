from elma.lgr import LGR_Image
from elma.lgr import LGR
from elma.constants import LGR_MANDATORY_FILES
from elma.constants import LGR_LIMITED_SIZE_FILES
from elma.constants import LGR_OBJECT_NAME
import io

LGR_PCX_MIN=10    #unused as practically never important
LGR_PCX_MAX=3500    #unused as practically never important
LGR_PCX_FILESIZE_MIN=1    #unused as practically never important
LGR_PCX_FILESIZE_MAX=10000000
LGR_PIC_MAX=999
LGR_PIC_WIDTH_MAX=6000
LGR_PIC_SIZE_MAX=600000
LGR_TEX_MIN=2
LGR_TEX_MAX=99
LGR_MASK_MAX=199
LGR_GRASS_MAX=99
LGR_OBJ_WIDTH=40
LGR_OBJ_HEIGHT=40
LGR_OBJ_FRAMES_MAX=1000
LGR_RECOMMEND_BIKE_WIDTH=354
LGR_RECOMMEND_BIKE_HEIGHT=298
LGR_WARNING_GRASS_HEIGHT_MIN=41
LGR_WARNING_QCOLORS_WIDTH=66
LGR_WARNING_QCOLORS_HEIGHT=109

ERR_LGR_INVALID_PALETTE=1
ERR_MISSING_MANDATORY_PCX=2
ERR_DUPLICATE_NAME=3
ERR_TOO_MANY_GRASS=4
ERR_TOO_MANY_TEXTURES=5
ERR_NOT_ENOUGH_TEXTURES=6
ERR_TOO_MANY_PICTURES=7
ERR_TOO_MANY_MASKS=8
WARN_UNUSED_FOOD=501

ERR_FILE_TOO_LARGE=1001
ERR_NAME_TOO_LONG=1002
ERR_NAME_MISSING=1003
ERR_PADDING=1004
ERR_IMAGE_TYPE=1005
ERR_DISTANCE=1006
ERR_TRANSPARENCY=1007
ERR_TOO_WIDE=1008
ERR_TOO_LARGE=1009
ERR_OBJ_WIDTH=1010
ERR_OBJ_TOO_WIDE=1011
ERR_SMALL_IMAGE_ONLY=1012
ERR_INVALID_PALETTE=1013
ERR_IMG_MISSING=1014

WARN_OBJ_HEIGHT=5001
WARN_GRASS_HEIGHT=5002
WARN_PALETTE_MISMATCH=5003
WARN_QCOLOR_DIMENSIONS=5004
WARN_BIKE_SMALL=5005

def check_LGR_error(lgro,palette=None):
    """
    Returns a list of errors or warnings for an LGR object or LGR_Image object. If you pass an LGR_Image object, you can also put a palette that the object should have
    """
    message=[]
    if(type(lgro).__name__=="LGR"):
        use_palette=None
        if(len(lgro.palette)==768 and max(lgro.palette)<=255 and min(lgro.palette)>=0):
            use_palette=lgro.palette
        else:
            message.append([ERR_LGR_INVALID_PALETTE,None,"The LGR file has an invalid palette! Please set a palette using get_palette() on one of the images or using LGR_Image.default_palette()"])
        n_pic=0
        n_tex=0
        n_mask=0
        n_grass=0
        apples=[False,False,False,False,False,False,False,False,False]
        for item in LGR_MANDATORY_FILES:
            n_count=0
            for obj in lgro.images:
                if(item==obj.name.lower()):
                    n_count=1
                    break
            if(n_count==0):
                message.append([ERR_MISSING_MANDATORY_PCX,item,"The LGR file is missing a mandatory file: %s"%(item)])
        len_lgr=len(lgro.images)
        for i in range(len_lgr):
            namelower=lgro.images[i].name.lower()
            if(lgro.images[i].is_in_pictures_lst()):
                if(namelower[:4]=="qup_" or namelower[:6]=="qdown_"):
                    n_grass+=1
                elif((namelower in LGR_OBJECT_NAME) and namelower[:5]=="qfood"):
                    apples[int(namelower[5:6])-1]=True
                elif(lgro.images[i].image_type==LGR_Image.PICTURE):
                    n_pic+=1
                elif(lgro.images[i].image_type==LGR_Image.TEXTURE):
                    n_tex+=1
                elif(lgro.images[i].image_type==LGR_Image.MASK):
                    n_mask+=1
            else:
                if(namelower=="qgrass"):
                    n_tex+=1

            for j in range(i+1,len_lgr,1):
                if(namelower==lgro.images[j].name.lower()):
                        message.append([ERR_DUPLICATE_NAME,lgro.images[j],"The LGR file has a duplicate of the following filename: %s"%(lgro.images[j].name)])
            message_temp=check_LGR_error(lgro.images[i],use_palette)
            if(message_temp):
                message.extend(message_temp)
        if(n_grass>LGR_GRASS_MAX):
            message.append([ERR_TOO_MANY_GRASS,n_grass,"The LGR file has %s grass images but can only support %s at most"%(n_grass,LGR_GRASS_MAX)])
        if(n_pic>LGR_PIC_MAX):
            message.append([ERR_TOO_MANY_PICTURES,n_pic,"The LGR file has %s picture images but can only support %s at most"%(n_pic,LGR_PIC_MAX)])
        if(n_tex<LGR_TEX_MIN):
            message.append([ERR_NOT_ENOUGH_TEXTURES,n_tex,"The LGR file has %s texture images but needs at least %s"%(n_tex,LGR_TEX_MIN)])
        elif(n_tex>LGR_TEX_MAX):
            message.append([ERR_TOO_MANY_TEXTURES,n_tex,"The LGR file has %s texture images but can only support %s at most"%(n_tex,LGR_TEX_MAX)])
        if(n_mask>LGR_MASK_MAX):
            message.append([ERR_TOO_MANY_MASKS,n_mask,"The LGR file has %s mask images but can only support %s at most"%(n_mask,LGR_MASK_MAX)])
        appleFinished=False
        for i in range(9):
            if(apples[i]):
                if(appleFinished):
                    message.append([WARN_UNUSED_FOOD,None,"Warning: qfood%s will not appear in the game as qfood%s is missing"%(i+1,i)])
            else:
                appleFinished=True
            
        return message
    elif(type(lgro).__name__=="LGR_Image"):
        is_mask=False
        len_name=len(lgro.name)
        if(len_name>8):
            message.append([ERR_NAME_TOO_LONG,lgro,"The name of %s is too long (maximum 8 characters)"%(lgro.name)])
        if(len_name==0):
            message.append([ERR_NAME_MISSING,lgro,"An LGR_Image has no name! %s"%(lgro)])
        try:
            if(len(bytes(lgro.padding))!=7):
                message.append([ERR_PADDING,lgro,"%s's padding is invalid (must be an array of 7 ints in range (0-255))"%(lgro.name)])
        except ValueError:
            message.append([ERR_PADDING,lgro,"%s's padding is invalid (must be an array of 7 ints in range (0-255))"%(lgro.name)])
        namelower=lgro.name.lower()
        if(lgro.is_in_pictures_lst()):
                if(namelower[:4]=="qup_" or namelower[:6]=="qdown_"):
                    if(lgro.img.height<LGR_WARNING_GRASS_HEIGHT_MIN):
                        message.append([WARN_GRASS_HEIGHT,lgro,"Warning: %s should have a minimum height of %s, but the height is %s"%(lgro.name,LGR_WARNING_GRASS_HEIGHT_MIN,lgro.img.height)])
                elif((namelower in LGR_OBJECT_NAME) and namelower[:5]=="qfood"):
                    if(lgro.img.height!=LGR_OBJ_HEIGHT):
                        message.append([WARN_OBJ_HEIGHT,lgro,"Warning: %s should have a height of %s, but the height is %s. If the height is smaller, the program might crash unexpectedly. If the height is larger, the additional columns will be ignored."%(lgro.name,LGR_OBJ_HEIGHT,lgro.img.height)])
                    if(lgro.img.width%LGR_OBJ_WIDTH!=0):
                        message.append([ERR_OBJ_WIDTH,lgro,"As %s is an object, the width (%s) must be a multiple of %s"%(lgro.name,lgro.img.width,LGR_OBJ_WIDTH)])
                    if(lgro.img.width>LGR_OBJ_WIDTH*LGR_OBJ_FRAMES_MAX):
                        message.append([ERR_OBJ_TOO_WIDE,lgro,"%s must have a width at most %s, but the width is %s"%(lgro.name,lgro.img.width,LGR_OBJ_WIDTH*LGR_OBJ_FRAMES_MAX)])
                else:
                    if(100>lgro.image_type<102):
                        message.append([ERR_IMAGE_TYPE,lgro,"%s's image_type is invalid"%(lgro.name)])
                    else:
                        if(lgro.image_type==LGR_Image.PICTURE):
                            if(lgro.img.width>LGR_PIC_WIDTH_MAX):
                                message.append([ERR_TOO_WIDE,lgro,"%s is too wide (%s) - the maximum is %s"%(lgro.name,lgro.width,LGR_PIC_WIDTH_MAX)])
                            if(lgro.img.width*lgro.img.height>LGR_PIC_SIZE_MAX):
                                message.append([ERR_TOO_LARGE,lgro,"%s has too many pixels (%s) - the maximum is %s. Depending on the image, the game might crash"%(lgro.name,lgro.img.width*lgro.img.height,LGR_PIC_SIZE_MAX)])
                        elif(lgro.image_type==LGR_Image.MASK):
                            is_mask=True
                    if(1>lgro.default_distance<999 and not(is_mask)):
                        message.append([ERR_DISTANCE,lgro,"%s's distance is invalid (must be integer between 1-999)"%(lgro.name)])
                    if(0>lgro.default_clipping<2 and not(is_mask)):
                        message.append([ERR_DISTANCE,lgro,"%s's clipping is invalid"%(lgro.name)])
                    if(11>lgro.transparency<15):
                        message.append([ERR_TRANSPARENCY,lgro,"%s's transparency is invalid"%(lgro.name)])
            
        if(lgro.img):
            with io.BytesIO() as f:
                lgro.save_PCX(f)
                size=f.tell()
                if(size>LGR_PCX_FILESIZE_MAX):
                    message.append([ERR_FILE_TOO_LARGE,lgro,"The file produced by %s is %s bytes in size, over the limit of %s"%(lgro.name,size,LGR_PCX_FILESIZE_MAX)])
            if((namelower in LGR_LIMITED_SIZE_FILES) and ((lgro.img.width>255)or(lgro.img.height>255))):
                message.append([ERR_SMALL_IMAGE_ONLY,lgro,"%s must have dimensions at most 255x255, but the dimensions are %sx%s"%(lgro.name,lgro.img.width,lgro.img.height)])
            if(lgro.is_valid_palette_image()):
                if(palette and not(is_mask) and (lgro.get_palette()!=palette)):
                    message.append([WARN_PALETTE_MISMATCH,lgro,"Warning: %s's palette does not match the LGR's palette!"%(lgro.name)])
            else:
                message.append([ERR_INVALID_PALETTE,lgro,"%s has an invalid palette"%(lgro.name)])
            if(namelower=="qcolors"):
                if(lgro.img.width!=LGR_WARNING_QCOLORS_WIDTH or lgro.img.height!=LGR_WARNING_QCOLORS_HEIGHT):
                    message.append([WARN_QCOLOR_DIMENSIONS,lgro,"Warning: qcolors usually has dimensions of %sx%s, but the dimensions are %sx%s"%(LGR_WARNING_QCOLORS_WIDTH,LGR_WARNING_QCOLORS_HEIGHT,lgro.img.width,lgro.img.height)])
            if(namelower=="q1bike" or namelower=="q2bike"):
                if(lgro.img.width<LGR_RECOMMEND_BIKE_WIDTH or lgro.img.height<LGR_RECOMMEND_BIKE_HEIGHT):
                    message.append([WARN_BIKE_SMALL,lgro,"Warning: %s needs dimensions of at least %sx%s to be rendered properly, but the dimensions are %sx%s"%(lgro.name,LGR_RECOMMEND_BIKE_WIDTH,LGR_RECOMMEND_BIKE_HEIGHT,lgro.img.width,lgro.img.height)])
        else:
            message.append([ERR_IMG_MISSING,lgro,"%s has no image!"%(lgro.name)])
    else:
        raise ValueError("only LGR and LGR_Image objects can be evaluated with this function")
    return message
        