from LZ77 import *
from ImageFunctions import *

import pygame
pygame.init()
        
class SpriteTab(wx.Panel):
    def __init__(self, parent, rom=None):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        self.rom = rom
        
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.generate_UI()
        
        self.SetSizer(self.sizer)

    def generate_UI(self):
        palette = LZUncompress(self.rom, 0xD2FE78)
        image = LZUncompress(self.rom, 0xD2FBD4)
        
        Compressed = LZCompress(image)

        self.rom.seek(0x760000)
        self.rom.write(Compressed)
        
        image = LZUncompress(self.rom, 0x760000)
        
        pal = ConvertGBAPalTo25Bit(palette)
        bmp = ConvertGBAImageToNormal(image,pal)
        bmp.SaveFile("Resources\\PokeFront.png", wx.BITMAP_TYPE_PNG)
        
        static_image = wx.StaticBitmap(self,-1,bmp)
        self.PositionEditor()
        
    def PositionEditor(self):
        #origin for pokeback is (40,48)
        #origin for pokefront is (144,8)
        
        pygame.display.set_caption("Position Editor", "Resources\\PokeSquare.png")
        pygame.display.set_icon(pygame.image.load("Resources\\PokeSquare.png"))
        size = width, height = 240,160
        screen = pygame.display.set_mode(size)
        BG = pygame.image.load("Resources\\BattleBG.png")
        
        PokeFront = pygame.image.load("Resources\\PokeFront.png")
        transparent_color = PokeFront.get_at((0,0))
        PokeFront.set_colorkey(transparent_color)
        
        TEXTBOX = pygame.image.load("Resources\\BattleTextBox.png")
        
        screen.blit(BG,pygame.Rect(0,0,240,160))
        screen.blit(PokeFront,pygame.Rect(144,8,64,64))
        screen.blit(TEXTBOX,pygame.Rect(0,0,240,160))
        pygame.display.flip()
        
        
        
        