from LZ77 import *
from ImageFunctions import *

class SpriteTab(wx.Panel):
    def __init__(self, parent, rom=None):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        self.rom = rom
        
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.generate_UI()
        
        self.SetSizer(self.sizer)

    def generate_UI(self):
        palette = LZUncompress(self.rom, 0xD2FE78)
        image = LZUncompress(self.rom, 0xD2FBD4)
        
        import binascii
        
        pal = ConvertGBAPalTo25Bit(palette)
        bmp = ConvertGBAImageToNormal(image,pal)
        
        
        static_image = wx.StaticBitmap(self,-1,bmp)
        
        self.sizer.Add(static_image, 1, wx.LEFT | wx.BOTTOM | wx.TOP, 10)