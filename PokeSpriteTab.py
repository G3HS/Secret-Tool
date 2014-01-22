from LZ77 import *
from ImageFunctions import *
from rom_insertion_operations import *
import os,time

import pygame
pygame.init()
        
class SpriteTab(wx.Panel):
    def __init__(self, parent, rom=None, config=None, rom_id=None):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        self.rom_name = rom
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
        
        PositionPanel = wx.Panel(self, -1, style=wx.RAISED_BORDER|wx.TAB_TRAVERSAL)
        PositionPanelSizer = wx.BoxSizer(wx.VERTICAL)
        PositionPanel.SetSizer(PositionPanelSizer)
        self.sizer.Add(PositionPanel, 0, wx.EXPAND | wx.ALL, 5)
        
        PositionEntrySizer = wx.GridBagSizer(3,3)
        PositionPanelSizer.Add(PositionEntrySizer, 0, wx.EXPAND | wx.ALL, 5)
        
        PlayerY_txt = wx.StaticText(PositionPanel, -1,"Player Y:")
        PositionEntrySizer.Add(PlayerY_txt, (0, 0), wx.DefaultSpan,  wx.ALL, 6)
        self.PlayerY = wx.TextCtrl(PositionPanel, -1,style=wx.TE_CENTRE, size=(40,-1))
        self.PlayerY.Bind(wx.EVT_TEXT, self.ChangeEntry)
        PositionEntrySizer.Add(self.PlayerY,(0, 1), wx.DefaultSpan,  wx.ALL, 4)
        
        EnemyY_txt = wx.StaticText(PositionPanel, -1,"Enemy Y:")
        PositionEntrySizer.Add(EnemyY_txt, (1, 0), wx.DefaultSpan,  wx.ALL, 6)
        self.EnemyY = wx.TextCtrl(PositionPanel, -1,style=wx.TE_CENTRE, size=(40,-1))
        self.EnemyY.Bind(wx.EVT_TEXT, self.ChangeEntry)
        PositionEntrySizer.Add(self.EnemyY,(1, 1), wx.DefaultSpan,  wx.ALL, 4)
        
        EnemyAlt_txt = wx.StaticText(PositionPanel, -1,"Enemy Altitude:")
        PositionEntrySizer.Add(EnemyAlt_txt, (2, 0), wx.DefaultSpan,  wx.ALL, 6)
        self.EnemyAlt = wx.TextCtrl(PositionPanel, -1,style=wx.TE_CENTRE, size=(40,-1))
        self.EnemyAlt.Bind(wx.EVT_TEXT, self.ChangeEntry)
        PositionEntrySizer.Add(self.EnemyAlt,(2, 1), wx.DefaultSpan,  wx.ALL, 4)
        
        GUIEditor = wx.Button(PositionPanel, 0, "Graphic Position Editor")
        self.Bind(wx.EVT_BUTTON, self.PositionEditor, id=0)
        PositionPanelSizer.Add(GUIEditor, 0, wx.EXPAND | wx.ALL, 2)
        
        self.load_everything(self.poke_num)
        
    def ChangeEntry(self, instance):
        instance = instance.GetEventObject()
        try: value = int(instance.GetValue(),0)
        except:
            limit = instance.GetValue()[:-1]
            curr = instance.GetValue()
            if curr != "0x" and curr != "" and curr != "-0x" and curr != "-":
                instance.SetValue(limit)
            return
            
        if value > 127:
            instance.SetValue("127")
        if value < 0:
            instance.SetValue("0")
        
    def load_everything(self, poke_num):
        self.poke_num = poke_num
        
        FrontSpriteTable = int(self.config.get(self.rom_id, "FrontSpriteTable"), 0)
        BackSpriteTable = int(self.config.get(self.rom_id, "BackSpriteTable"), 0)
        FrontPaletteTable = int(self.config.get(self.rom_id, "FrontPaletteTable"), 0)
        ShinyPaletteTable = int(self.config.get(self.rom_id, "ShinyPaletteTable"), 0)
        enemyytable = int(self.config.get(self.rom_id, "enemyytable"), 0)
        playerytable = int(self.config.get(self.rom_id, "playerytable"), 0)
        enemyaltitudetable = int(self.config.get(self.rom_id, "enemyaltitudetable"), 0)
        iconspritetable = int(self.config.get(self.rom_id, "iconspritetable"), 0)
        iconpalettetable = int(self.config.get(self.rom_id, "iconpalettetable"), 0)
        iconpalettes = int(self.config.get(self.rom_id, "iconpalettes"), 0)
        
        bytes_per_entry = 8 ##Need to load from ini for EMERALD
        
        with open(self.rom_name, "r+") as rom:
            rom.seek(FrontSpriteTable+(poke_num+1)*bytes_per_entry)
            self.FrontSpritePointer = read_pointer(rom.read(4))
            rom.seek(BackSpriteTable+(poke_num+1)*bytes_per_entry)
            self.BackSpritePointer = read_pointer(rom.read(4))
            rom.seek(FrontPaletteTable+(poke_num+1)*bytes_per_entry)
            self.FrontPalettePointer = read_pointer(rom.read(4))
            rom.seek(ShinyPaletteTable+(poke_num+1)*bytes_per_entry)
            self.ShinyPalettePointer = read_pointer(rom.read(4))
        
            FrontSprite = LZUncompress(rom, self.FrontSpritePointer)
            BackSprite = LZUncompress(rom, self.BackSpritePointer)
            FrontPalette = LZUncompress(rom, self.FrontPalettePointer)
            ShinyPalette = LZUncompress(rom, self.ShinyPalettePointer)

            FrontPalette = ConvertGBAPalTo25Bit(FrontPalette)
            ShinyPalette = ConvertGBAPalTo25Bit(ShinyPalette)
            
            self.TMPFrontSprite = ConvertGBAImageToNormal(FrontSprite,FrontPalette)
            self.TMPBackSprite = ConvertGBAImageToNormal(BackSprite,FrontPalette)
            self.TMPSFrontSprite = ConvertGBAImageToNormal(FrontSprite,ShinyPalette)
            self.TMPSBackSprite = ConvertGBAImageToNormal(BackSprite,ShinyPalette)
            
            self.FrontSprite.SetBitmap(self.TMPFrontSprite)
            self.BackSprite.SetBitmap(self.TMPBackSprite)
            self.SFrontSprite.SetBitmap(self.TMPSFrontSprite)
            self.SBackSprite.SetBitmap(self.TMPSBackSprite)
            
            rom.seek(playerytable+(poke_num+1)*4+1)
            PlayerY = deal_with_8bit_signed_hex(int(get_bytes_string_from_hex_string(rom.read(1)),16))
            self.PlayerY.SetValue(str(PlayerY))
            
            rom.seek(enemyaltitudetable+(poke_num+1))
            EnemyAlt = deal_with_8bit_signed_hex(int(get_bytes_string_from_hex_string(rom.read(1)),16))
            self.EnemyAlt.SetValue(str(EnemyAlt))
            
            rom.seek(enemyytable+(poke_num+1)*4+1)
            EnemyY = deal_with_8bit_signed_hex(int(get_bytes_string_from_hex_string(rom.read(1)),16))
            self.EnemyY.SetValue(str(EnemyY))
        
        
    def PositionEditor(self, instance):
        #origin for pokeback is (40,48)
        #origin for pokefront is (144,8)
        self.TMPFrontSprite.SaveFile(os.path.join("Resources","PokeFront.png"), wx.BITMAP_TYPE_PNG)
        self.TMPBackSprite.SaveFile(os.path.join("Resources","PokeBack.png"), wx.BITMAP_TYPE_PNG)
        
        #Get Key Mappings:
        self.PlayerYUp = (str(self.config.get("ALL", "PlayerYUp")), "PUp")
        self.PlayerYDown = (str(self.config.get("ALL", "PlayerYDown")), "PDown")
        self.EnemyYUp = (str(self.config.get("ALL", "EnemyYUp")), "EUp")
        self.EnemyYDown = (str(self.config.get("ALL", "EnemyYDown")), "EDown")
        self.EnemyAltUp = (str(self.config.get("ALL", "EnemyAltUp")), "EAUp")
        self.EnemyAltDown = (str(self.config.get("ALL", "EnemyAltDown")), "EADown")
        Mappings = [self.PlayerYUp,self.PlayerYDown,self.EnemyYUp,self.EnemyYDown,self.EnemyAltUp,self.EnemyAltDown]
        
        listofkeys = [pygame.K_BACKSPACE,pygame.K_TAB,pygame.K_CLEAR,pygame.K_RETURN,pygame.K_PAUSE,
            pygame.K_ESCAPE,pygame.K_SPACE ,pygame.K_EXCLAIM,pygame.K_QUOTEDBL,pygame.K_HASH,
            pygame.K_DOLLAR,pygame.K_AMPERSAND,pygame.K_QUOTE,pygame.K_LEFTPAREN,
            pygame.K_RIGHTPAREN,pygame.K_ASTERISK,pygame.K_PLUS,pygame.K_COMMA,pygame.K_MINUS,
            pygame.K_PERIOD,pygame.K_SLASH,pygame.K_0,pygame.K_1,pygame.K_2,pygame.K_3,pygame.K_4,
            pygame.K_5,pygame.K_6,pygame.K_7,pygame.K_8,pygame.K_9,pygame.K_COLON,
            pygame.K_SEMICOLON,pygame.K_LESS,pygame.K_EQUALS,pygame.K_GREATER,pygame.K_QUESTION,
            pygame.K_AT,pygame.K_LEFTBRACKET,pygame.K_BACKSLASH,pygame.K_RIGHTBRACKET,pygame.K_CARET,
            pygame.K_UNDERSCORE,pygame.K_BACKQUOTE,pygame.K_a,pygame.K_b,pygame.K_c,
            pygame.K_d,pygame.K_e,pygame.K_f,pygame.K_g,pygame.K_h,pygame.K_i,pygame.K_j,pygame.K_k,
            pygame.K_l,pygame.K_m,pygame.K_n,pygame.K_o,pygame.K_p,pygame.K_q,pygame.K_r,pygame.K_s,
            pygame.K_t,pygame.K_u,pygame.K_v,pygame.K_w,pygame.K_x,pygame.K_y,pygame.K_z,pygame.K_DELETE,
            pygame.K_KP0,pygame.K_KP1,pygame.K_KP2,pygame.K_KP3,pygame.K_KP4,pygame.K_KP5,pygame.K_KP6,
            pygame.K_KP7,pygame.K_KP8,pygame.K_KP9,pygame.K_KP_PERIOD,pygame.K_KP_DIVIDE,pygame.K_KP_MULTIPLY,
            pygame.K_KP_MINUS,pygame.K_KP_PLUS,pygame.K_KP_ENTER,pygame.K_KP_EQUALS,pygame.K_UP,pygame.K_DOWN,
            pygame.K_RIGHT,pygame.K_LEFT,pygame.K_INSERT,pygame.K_HOME,pygame.K_END,pygame.K_PAGEUP,
            pygame.K_PAGEDOWN,pygame.K_F1,pygame.K_F2,pygame.K_F3,pygame.K_F4,pygame.K_F5,pygame.K_F6,pygame.K_F7,
            pygame.K_F8,pygame.K_F9,pygame.K_F10,pygame.K_F11,pygame.K_F12,pygame.K_F13,pygame.K_F14,pygame.K_F15,
            pygame.K_NUMLOCK,pygame.K_CAPSLOCK,pygame.K_SCROLLOCK,pygame.K_RSHIFT,pygame.K_LSHIFT,
            pygame.K_RCTRL,pygame.K_LCTRL,pygame.K_RALT,pygame.K_LALT,pygame.K_RMETA,pygame.K_LMETA,pygame.K_LSUPER,
            pygame.K_RSUPER,pygame.K_MODE,pygame.K_HELP,pygame.K_PRINT,pygame.K_SYSREQ,pygame.K_BREAK,
            pygame.K_MENU,pygame.K_POWER,pygame.K_EURO]
        
        self.Mappings = []
        for key in listofkeys:
            for map in Mappings:
                if pygame.key.name(key) == map[0]:
                    self.Mappings.append((key, map[1]))
        pygame.display.set_caption("Position Editor", os.path.join("Resources","PokeSquare.png"))
        pygame.display.set_icon(pygame.image.load(os.path.join("Resources","PokeSquare.png")))
        size = width, height = 240,160
        self.screen = pygame.display.set_mode(size)
        self.PYGBG = pygame.image.load(os.path.join("Resources","BattleBG.png"))
        
        self.PYGPokeFront = pygame.image.load(os.path.join("Resources","PokeFront.png"))
        transparent_color = self.PYGPokeFront.get_at((0,0))
        self.PYGPokeFront.set_colorkey(transparent_color)
        
        alt = int(self.EnemyAlt.GetValue(),0)
        
        self.shadow = pygame.image.load(os.path.join("Resources","Shadow.png"))
        self.shadow_rect = pygame.Rect(160,65,32,8)
        FrontHeight = 8+int(self.EnemyY.GetValue(),0)-alt
        PokeFrontRect = pygame.Rect(144,FrontHeight,64,64)
        
        self.PYGPokeBack = pygame.image.load(os.path.join("Resources","PokeBack.png"))
        transparent_color = self.PYGPokeBack.get_at((0,0))
        self.PYGPokeBack.set_colorkey(transparent_color)
        
        BackHeight = 48+int(self.PlayerY.GetValue(),0)
        PokeBackRect = pygame.Rect(40,BackHeight,64,64)
        
        self.PYGTEXTBOX = pygame.image.load(os.path.join("Resources","BattleTextBox.png"))
        
        self.screen.blit(self.PYGBG,pygame.Rect(0,0,240,160))
        if alt > 0:
            self.screen.blit(self.PYGPokeBack,self.shadow_rect)
        self.screen.blit(self.shadow,PokeFrontRect)
        self.screen.blit(self.PYGPokeBack,PokeBackRect)
        self.screen.blit(self.PYGTEXTBOX,pygame.Rect(0,0,240,160))
        pygame.display.flip()
        self.set_timer()

        
    def on_timer(self, event):
        self.set_timer()
        self.PositionEditorLoop()

    def set_timer(self):
        TIMER_ID = 1  # pick a number
        self.timer = wx.Timer(self, TIMER_ID)  # message will be sent to the panel
        self.timer.Start(100)  # x500 milliseconds
        wx.EVT_TIMER(self, TIMER_ID, self.on_timer)  # call the on_timer function
        
    def PositionEditorLoop(self, *args):
        need_update = []
        pygame.event.pump()
        keys = pygame.key.get_pressed()
        for map in self.Mappings:
            if keys[map[0]]:
                need_update.append(map[1])
        for need in need_update:
            if need == "PUp":
                try:
                    curr = int(self.PlayerY.GetValue(),0)
                    curr -= 1
                    self.PlayerY.SetValue(str(curr))
                    print self.PlayerY.GetValue()
                    #time.sleep(0.15)
                except: pass
            elif need == "PDown":
                try:
                    curr = int(self.PlayerY.GetValue(),0)
                    curr += 1
                    self.PlayerY.SetValue(str(curr))
                    #time.sleep(0.1)
                except: pass
            elif need == "EUp":
                try:
                    curr = int(self.EnemyY.GetValue(),0)
                    curr -= 1
                    self.EnemyY.SetValue(str(curr))
                    #time.sleep(0.1)
                except: pass
            elif need == "EDown":
                try:
                    curr = int(self.EnemyY.GetValue(),0)
                    curr += 1
                    self.EnemyY.SetValue(str(curr))
                    #time.sleep(0.1)
                except: pass
            elif need == "EAUp":
                try:
                    curr = int(self.EnemyAlt.GetValue(),0)
                    curr -= 1
                    self.EnemyAlt.SetValue(str(curr))
                    #time.sleep(0.1)
                except: pass
            elif need == "EADown":
                try:
                    curr = int(self.EnemyAlt.GetValue(),0)
                    curr += 1
                    self.EnemyAlt.SetValue(str(curr))
                    #time.sleep(0.1)
                except: pass
        self.UpdatePosition()
                
    def UpdatePosition(self):
        try:
            alt = int(self.EnemyAlt.GetValue(),0)
            FrontHeight = 8+int(self.EnemyY.GetValue(),0)-alt
            PokeFrontRect = pygame.Rect(144,FrontHeight,64,64)
            
            BackHeight = 48+int(self.PlayerY.GetValue(),0)
            PokeBackRect = pygame.Rect(40,BackHeight,64,64)
            
            self.screen.blit(self.PYGBG,pygame.Rect(0,0,240,160))
            if alt > 0:
                self.screen.blit(self.shadow,self.shadow_rect)
            self.screen.blit(self.PYGPokeFront,PokeFrontRect)
            self.screen.blit(self.PYGPokeBack,PokeBackRect)
            self.screen.blit(self.PYGTEXTBOX,pygame.Rect(0,0,240,160))
            pygame.display.flip()
        except: pass
        