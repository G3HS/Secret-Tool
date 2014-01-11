from binascii import hexlify, unhexlify
import wx

def ConvertGBAPalTo25Bit(palette):
    ##Palette should be in the form of "\xFF\xFF\xFF\xFF..."
    blue_mask = 0x7C00
    green_mask = 0x3E0
    red_mask = 0x1F
    
    count = 0
    new_palette = []
    for n in range(len(palette)/2):
        color = palette[count+1]+palette[count]
        color = hexlify(color)
        color = int(color,16)
        
        red = (color & red_mask)
        green = (color & green_mask) >> 5
        blue = (color & blue_mask) >> 10
        
        red = red << 3
        green = green << 3
        blue = blue << 3
        
        new_color = [red,green,blue]
        new_palette.append(new_color)
        count += 2
    return new_palette
    
def ConvertGBAImageToNormal(image, palette, size=(64,64)):
    indexed_image = []
    for c in image:
        pixels = hexlify(c)
        pixela = int(pixels[1],16)
        pixelb = int(pixels[0],16)
        indexed_image.append(pixela)
        indexed_image.append(pixelb)
    
    blocks = []
    n = 0
    for z in range(64):
        tmp_list = indexed_image[n:n+64]
        blocks.append(tmp_list)
        n += 64
    #create first 8 rows
    image_data = []
    b = 0
    a = 0
    row = 0
    for n in range(size[0]/8):
        for n in range(size[1]/8):
            b = row
            for n in range(size[1]/8):
                r = 0
                for n in range(8):
                    image_data.append(blocks[b][a+r])
                    r += 1
                b += 1
            a += 8
        a = 0
        row += 8
    img_data = []
    for pixel in image_data:
        img_data.append(palette[pixel][0]) #Append Red
        img_data.append(palette[pixel][1]) #Append Green
        img_data.append(palette[pixel][2]) #Append Blue

    data = ""
    for color in img_data:
        data += unhexlify(hex(color)[2:].zfill(2))
    img = wx.ImageFromData(size[0], size[1], data)
    bitmap = wx.BitmapFromImage(img)
    return bitmap
