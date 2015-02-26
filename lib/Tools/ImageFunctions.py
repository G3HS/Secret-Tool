from binascii import hexlify, unhexlify
import wx,math

def ConvertGBAPalTo25Bit(palette):
    """
    Take a GBA palette and convert it to a normal
    25bit RGB palette. This function will return a
    list of tuples like (Red, Green, Blue).
    
    Palette should be in the form of "\xFF\xFF\xFF\xFF..."
    """
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

def Convert25bitPalettetoGBA(palette):
    """
    This function will take a list of tuples of RGB values
    and convert them back into the GBA format.
    
    It will return a bytestring of length 32.
    
    This function is only for 16 color sprites.
    """
    GBAPal = ""
    for color in palette:
        red = color[0]
        green = color[1]
        blue = color[2]
        
        red = red >> 3
        green = green >> 3
        blue = blue >> 3
        
        green = green << 5
        blue = blue << 10
        
        color = (blue | green | red)
        hexColor = hex(color).rstrip("L").lstrip("0x").zfill(4)
        bytes = unhexlify(hexColor)
        bytes = bytes[1]+bytes[0]
        GBAPal += bytes
    for i in range(len(palette)*2-len(GBAPal)):
        GBAPal += "\x00"
    return GBAPal
    
def ConvertGBAImageToNormal(image, palette, size=(64,64)):
    """
    This will take a GBA image in the form of a byte string
    like "\xff\xe0\x22..." and convert it to a normal RGB image.
    
    Because GBA images are stored in 8x8 tiles, there are a lot of
    loops in the function.:P
    """
    
    indexed_image = []
    for c in image:
        pixels = hexlify(c)
        pixela = int(pixels[1],16)
        pixelb = int(pixels[0],16)
        indexed_image.append(pixela)
        indexed_image.append(pixelb)
    width = size[0]
    height = size[1]
    NumOfBlocks = (width/8) * (height/8)
    blocks = []
    n = 0
    for z in range(NumOfBlocks):
        tmp_list = indexed_image[n:n+64]
        blocks.append(tmp_list)
        n += 64
    image_data = []
    b = 0
    a = 0
    row = 0
    for x in range(height/8):
        for y in range(8):
            b = row
            for z in range(width/8):
                r = 0
                for w in range(8):
                    image_data.append(blocks[b][a+r])
                    r += 1
                b += 1
            a += 8
        a = 0
        row += width/8
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

def ConvertGBAFootprintToNormal(footprint,size=(16,16)):
    """
    This will take a GBA footprint in the form of a byte string
    like "\xff\xe0\x22..." and convert it to a normal RGB image.
    
    Because GBA images are stored in 8x8 tiles, there are a lot of
    loops in the function.:P
    """
    palette = [(200,200,255),(0,0,0)]
    indexed_image = []
    binary = ""
    for n in footprint:
        binary += bin(int(hexlify(n),16)).lstrip("0b").rstrip("L").zfill(8)[::-1]
    image = unhexlify(binary)
    for c in image:
        pixels = hexlify(c)
        pixela = int(pixels[0],16)
        pixelb = int(pixels[1],16)
        indexed_image.append(pixela)
        indexed_image.append(pixelb)
    width = size[0]
    height = size[1]
    NumOfBlocks = (width/8) * (height/8)
    blocks = []
    n = 0
    for z in range(NumOfBlocks):
        tmp_list = indexed_image[n:n+64]
        blocks.append(tmp_list)
        n += 64
    image_data = []
    b = 0
    a = 0
    row = 0
    for x in range(height/8):
        for y in range(8):
            b = row
            for z in range(width/8):
                r = 0
                for w in range(8):
                    image_data.append(blocks[b][a+r])
                    r += 1
                b += 1
            a += 8
        a = 0
        row += width/8
    img_data = []
    for pixel in image_data:
        img_data.append(palette[pixel][0]) #Append Red
        img_data.append(palette[pixel][1]) #Append Green
        img_data.append(palette[pixel][2]) #Append Blue

    data = ""
    for color in img_data:
        data += unhexlify(hex(color)[2:].zfill(2))
    img = wx.ImageFromData(size[0], size[1], data)
    img = img.Scale(64, 64)
    bitmap = wx.BitmapFromImage(img)
    return bitmap

def ConvertNormalFootPrintToGBA(image):
    """
    This function will take a normal wx.Image and return a gba footprint.
    Image must be already 2 colors and have dimensions of 16x16.
    """
    data = image.GetData()
    height = 16
    width = 16
    blocks = []
    block_num = width/8
    for w in range(height/8):
        for x in range(8):
            block_num -= width/8
            for y in range(width/8):
                for z in range(8):
                    color = [int(hexlify(data[:1]),16),
                                  int(hexlify(data[1:2]),16),
                                  int(hexlify(data[2:3]),16)]
                    try: blocks[block_num]
                    except: blocks.append([])
                    blocks[block_num].append(color)
                    data = data[3:]
                block_num += 1
        block_num += width/8
    GBAImage = ""
    for block in blocks:
        counter = 0
        for x in range(8): #Per row
            binary = ""
            for x in range(8):
                if block[counter] == [255,255,255]:
                    binary += "0"
                else:
                    binary += "1"
                counter += 1
            binary = binary[::-1]
            integer = int(binary,2)
            hexteger  = hex(integer).lstrip("0x").rstrip("L").zfill(2)
            GBAImage += unhexlify(hexteger)
    return GBAImage

def ConvertNormalImageToGBA(image, palette=None, size=(64,64)):
    """
    This function will take a normal wx.Image and return tuple
    of (GBA_Image, Palette). Image must be already 16 colors
    and have dimensions divisible by 8.
    
    If a palette is provided, it will not make a new palette, instead
    using that one to find indexes.
    """
    if palette:
        dontmap = True
        if type(palette[0]) is list:
            tmp = palette
            palette = []
            for color in tmp:
                palette.append((color[0],color[1],color[2]))
    else:
        dontmap = False
        palette = []
    data = image.GetData()
    height = size[1]
    width = size[0]
    blocks = []
    block_num = width/8
    for w in range(height/8):
        for x in range(8):
            block_num -= width/8
            for y in range(width/8):
                for z in range(8):
                    color = [int(hexlify(data[:1]),16),
                                  int(hexlify(data[1:2]),16),
                                  int(hexlify(data[2:3]),16)]
                    if dontmap == False:
                        if color not in palette:
                            palette.append(color)
                    try: blocks[block_num]
                    except: blocks.append([])
                    blocks[block_num].append(color)
                    data = data[3:]
                block_num += 1
        block_num += width/8
    GBAImage = ""
    color1 = None
    color2 = None
    for block in blocks:
        for color in block:
            if color not in palette:
                color = best_match(color, palette)
            if color1 == None:
                color1 = hex(palette.index(color))[2:].zfill(1)
            else:
                color2 = hex(palette.index(color))[2:].zfill(1)
                GBAImage += unhexlify(color2+color1)
                color1 = None
                color2 = None
    while len(palette) < 16:
        palette.append((0,0,0))
    ListPalette = []
    for color in palette:
        ListPalette.append([color[0],color[1],color[2]])
    return (GBAImage, ListPalette)

def distance(color1, color2):
    return math.sqrt(sum([(e1-e2)**2 for e1, e2 in zip(color1, color2)]))
    
def best_match(sample, colors):
    by_distance = sorted(colors, key=lambda c: distance(c, sample))
    return by_distance[0]
    
def BestPalette(Palettes, ImagePal):
    BestPaletteTracker = []
    for pal in Palettes:
        BestPaletteTracker.append(0)
    for color in ImagePal:
        CurrentBestColor = []
        for pal in Palettes:
            CurrentBestColor.append(0)
        for num, pal in enumerate(Palettes):
            BestColor = best_match(color,pal)
            CurrentBestColor[num] = distance(color, BestColor)
        closest = min(CurrentBestColor)
        count = 0
        for x in CurrentBestColor:
            if x == closest:
                count += 1
        if count == 1:
            index = CurrentBestColor.index(closest)
            BestPaletteTracker[index] += 1
    return BestPaletteTracker.index(max(BestPaletteTracker))

def GetImageColors(image):
    palette = []
    data = image.GetData()
    for z in range(len(data)/3):
        color = [int(hexlify(data[:1]),16),
                 int(hexlify(data[1:2]),16),
                 int(hexlify(data[2:3]),16)]
        data = data[3:]
        palette.append(color)
    return palette
                    
def ConvertNormalImageToGBAUnderPal(image, palette,size=(64,64)):
    """
    This function will take a normal wx.Image and return tuple
    of (GBA_Image, Palette). Image must be already 16 colors
    and have dimensions divisible by 8.
    
    The difference between this function and the last is that a palette is provided
    to index to.
    """
    data = image.GetData()
    height = size[1]
    width = size[0]
    blocks = []
    block_num = width/8
    for w in range(height/8):
        for x in range(8):
            block_num -= width/8
            for y in range(width/8):
                for z in range(8):
                    color = (int(hexlify(data[:1]),16),
                                  int(hexlify(data[1:2]),16),
                                  int(hexlify(data[2:3]),16))
                    try: blocks[block_num]
                    except: blocks.append([])
                    blocks[block_num].append(color)
                    data = data[3:]
                block_num += 1
        block_num += width/8
    GBAImage = ""
    color1 = None
    color2 = None
    for block in blocks:
        for color in block:
            if color not in palette:
                color = best_match(color, palette)
            if color1 == None:
                color1 = hex(palette.index(color))[2:].zfill(1)
            else:
                color2 = hex(palette.index(color))[2:].zfill(1)
                GBAImage += unhexlify(color2+color1)
                color1 = None
                color2 = None
    return (GBAImage, palette)

def GetShinyPalette(normal, shiny, normal_palette):
    """
    This function helps to ensure that the shiny and 
    normal palettes are in the same order.
    
    Just pass it the normal and shiny images,
     along with the normal palette.
    """
    palette = []
    norm = list(normal.getdata())
    shin = list(shiny.getdata())
    misses = False
    for pixel in normal_palette:
        px = (pixel[0],pixel[1],pixel[2])
        try: 
            index = norm.index(px)
            palette.append([shin[index][0],shin[index][1],shin[index][2]])
        except:
            misses = True
    if misses:
        for color in shin:
            if color not in palette:
                if len(palette) < 16:
                    palette.append([color[0],color[1],color[2]])
                else:
                    break
    while len(palette) < 16:
        palette.append([0,0,0])
    return palette
        
