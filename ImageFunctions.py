from binascii import hexlify, unhexlify
import wx

def ConvertGBAPalTo25Bit(palette):
    ##Palette should be in the form of "\xFF\xFF\xFF\xFF..."
    red_mask = 0x7C00
    green_mask = 0x3E0
    blue_mask = 0x1F
    
    count = 0
    new_palette = []
    for n in range(len(palette)/2):
        color = palette[count+1]+palette[count]
        color = hexlify(color)
        color = int(color,16)
        
        red = (color & red_mask) >> 10
        green = (color & green_mask) >> 5
        blue = (color & blue_mask)
        
        red = red << 3
        green = green << 3
        blue = blue << 3
        
        new_color = (red << 10)+(green << 5)+(blue)
        new_palette.append(new_color)
    return new_palette
    
def ConvertGBAImageToNormal(image, palette, size=(64,64)):
    indexed_image = ""
    for c in image:
        pixels = int(hexlify(c),16)
        pixela = pixels & 0x0F
        pixelb = pixels & 0xF0 >> 4
        indexed_image += pixela
        indexed_image += pixelb
    img_data = []
    for pixel in indexed_image:
        img_data.append(palette[pixel])
    img = wx.ImageFromData(size[0], size[1], img_data)
    bitmap = wx.BitmapFromImage(img)
    return bitmap