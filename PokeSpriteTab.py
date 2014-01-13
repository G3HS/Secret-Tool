from LZ77 import *
from ImageFunctions import *
from rom_insertion_operations import *

import pygame
pygame.init()
        
class SpriteTab(wx.Panel):
    def __init__(self, parent, rom=None, config=None, rom_id=None):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        self.rom = rom
        self.config = config
        self.rom_id = rom_id
        self.poke_num = 0
        
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.generate_UI(self.poke_num)
        
        
        
        self.SetSizer(self.sizer)

    def generate_UI(self, poke_num):
        self.poke_num = poke_num
        spritePanel = wx.Panel(self, -1, style=wx.RAISED_BORDER|wx.TAB_TRAVERSAL)
        spritePanelSizer = wx.BoxSizer(wx.VERTICAL)
        spritePanel.SetSizer(spritePanelSizer)
        self.sizer.Add(spritePanel, 0, wx.EXPAND | wx.ALL, 5)
        
        self.FrontSprite = wx.StaticBitmap(spritePanel,-1,wx.EmptyBitmap(64,64))
        self.BackSprite = wx.StaticBitmap(spritePanel,-1,wx.EmptyBitmap(64,64))
        self.SFrontSprite = wx.StaticBitmap(spritePanel,-1,wx.EmptyBitmap(64,64))
        self.SBackSprite = wx.StaticBitmap(spritePanel,-1,wx.EmptyBitmap(64,64))
        
        spritePanelSizer.Add(self.FrontSprite, 0, wx.EXPAND | wx.ALL, 5)
        spritePanelSizer.Add(self.BackSprite, 0, wx.EXPAND | wx.ALL, 5)
        spritePanelSizer.Add(self.SFrontSprite, 0, wx.EXPAND | wx.ALL, 5)
        spritePanelSizer.Add(self.SBackSprite, 0, wx.EXPAND | wx.ALL, 5)
        
        self.load_everything(self.poke_num)
        
    def load_everything(self, poke_num):
        self.poke_num = poke_num
        
        FrontSpriteTable = int(self.config.get(self.rom_id, "FrontSpriteTable"), 0)
        BackSpriteTable = int(self.config.get(self.rom_id, "BackSpriteTable"), 0)
        FrontPaletteTable = int(self.config.get(self.rom_id, "FrontPaletteTable"), 0)
        ShinyPaletteTable = int(self.config.get(self.rom_id, "ShinyPaletteTable"), 0)
        
        bytes_per_entry = 8 ##Need to load from ini for EMERALD
        
        self.rom.seek(FrontSpriteTable+(poke_num+1)*bytes_per_entry)
        self.FrontSpritePointer = read_pointer(self.rom.read(4))
        self.rom.seek(BackSpriteTable+(poke_num+1)*bytes_per_entry)
        self.BackSpritePointer = read_pointer(self.rom.read(4))
        self.rom.seek(FrontPaletteTable+(poke_num+1)*bytes_per_entry)
        self.FrontPalettePointer = read_pointer(self.rom.read(4))
        self.rom.seek(ShinyPaletteTable+(poke_num+1)*bytes_per_entry)
        self.ShinyPalettePointer = read_pointer(self.rom.read(4))
        
        FrontSprite = LZUncompress(self.rom, self.FrontSpritePointer)
        BackSprite = LZUncompress(self.rom, self.BackSpritePointer)
        FrontPalette = LZUncompress(self.rom, self.FrontPalettePointer)
        ShinyPalette = LZUncompress(self.rom, self.ShinyPalettePointer)

        FrontPalette = ConvertGBAPalTo25Bit(FrontPalette)
        ShinyPalette = ConvertGBAPalTo25Bit(ShinyPalette)
        
        self.TMPFrontSprite = ConvertGBAImageToNormal(FrontSprite,FrontPalette)
        self.TMPBackSprite = ConvertGBAImageToNormal(BackSprite,FrontPalette)
        self.TMPSFrontSprite = ConvertGBAImageToNormal(FrontSprite,ShinyPalette)
        self.TMPSBackSprite = ConvertGBAImageToNormal(BackSprite,ShinyPalette)
        
        #bmp.SaveFile("Resources\\PokeFront.png", wx.BITMAP_TYPE_PNG)
        
        self.FrontSprite.SetBitmap(self.TMPFrontSprite)
        self.BackSprite.SetBitmap(self.TMPBackSprite)
        self.SFrontSprite.SetBitmap(self.TMPSFrontSprite)
        self.SBackSprite.SetBitmap(self.TMPSBackSprite)
        
        
        
        
    def PositionEditor(self, instance):
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
        
        
        
        