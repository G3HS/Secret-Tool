from LZ77 import *
from binascii import hexlify, unhexlify
from ImageFunctions import *
from rom_insertion_operations import *
import os,time
from PIL import Image
from PILandWXPythonConversions import *
from Button import *

import pygame

class SpriteTab(wx.Panel):
    def __init__(self, parent, rom=None, config=None, rom_id=None):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        self.rom_name = rom
        self.lastPath = os.path.dirname(self.rom_name)
        self.config = config
        self.rom_id = rom_id
        self.poke_num = 0
        self.OrgSizes = {}
        self.IconPalNum = 0
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.generate_UI(self.poke_num)

        self.SetSizer(self.sizer)

    def generate_UI(self, poke_num):
        self.poke_num = poke_num
        
        spritePanel = wx.Panel(self, -1, style=wx.RAISED_BORDER|wx.TAB_TRAVERSAL)
        spritePanelSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.Add(spritePanel, 0, wx.EXPAND | wx.ALL, 5)
        SpritesAndPals = wx.BoxSizer(wx.VERTICAL)
        spritePanel.SetSizer(SpritesAndPals)
        SpritesAndPals.Add(spritePanelSizer, 0, wx.EXPAND | wx.ALL, 0)
        
        LoadAllButton = Button(spritePanel, 60, "Load 256x64 Sheet")
        self.Bind(wx.EVT_BUTTON, self.LoadSheetSprite, id=60)
        SpritesAndPals.Add(LoadAllButton, 0, wx.EXPAND | wx.ALL, 6)
        
        self.cb = wx.CheckBox(spritePanel, -1, 'Fill sprites with 0xFF on repoint?', (10, 10))
        self.cb.SetValue(True)
        SpritesAndPals.Add(self.cb, 0, wx.ALL|wx.ALIGN_CENTER, 5)
        
        button_size = (76,76)
        self.FrontSprite = wx.BitmapButton(spritePanel,56,wx.EmptyBitmap(64,64), size=button_size)
        self.FrontSprite.SetCursor(wx.StockCursor(wx.CURSOR_HAND))
        self.BackSprite = wx.BitmapButton(spritePanel,57,wx.EmptyBitmap(64,64), size=button_size)
        self.BackSprite.SetCursor(wx.StockCursor(wx.CURSOR_HAND))
        self.SFrontSprite = wx.BitmapButton(spritePanel,58,wx.EmptyBitmap(64,64), size=button_size)
        self.SFrontSprite.SetCursor(wx.StockCursor(wx.CURSOR_HAND))
        self.SBackSprite = wx.BitmapButton(spritePanel,59,wx.EmptyBitmap(64,64), size=button_size)
        self.SBackSprite.SetCursor(wx.StockCursor(wx.CURSOR_HAND))
        
        self.Bind(wx.EVT_BUTTON, self.LoadSingleSprite, id=56)
        self.Bind(wx.EVT_BUTTON, self.LoadSingleSprite, id=57)
        self.Bind(wx.EVT_BUTTON, self.LoadSingleSprite, id=58)
        self.Bind(wx.EVT_BUTTON, self.LoadSingleSprite, id=59)
        
        sprite_border = 6
        spritePanelSizer.Add(self.FrontSprite, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, sprite_border)
        spritePanelSizer.Add(self.BackSprite, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, sprite_border)
        div = wx.StaticLine(spritePanel, -1, style=wx.LI_VERTICAL)
        div.SetSize((2,74))
        spritePanelSizer.Add(div, 0, wx.EXPAND | wx.ALL, 3)
        spritePanelSizer.Add(self.SFrontSprite, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, sprite_border)
        spritePanelSizer.Add(self.SBackSprite, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, sprite_border)
        
        PalettePanel = wx.Panel(spritePanel, -1, style=wx.RAISED_BORDER|wx.TAB_TRAVERSAL)
        PalettePanelSizer = wx.BoxSizer(wx.VERTICAL)
        PalettePanel.SetSizer(PalettePanelSizer)
        SpritesAndPals.Add(PalettePanel, 0, wx.EXPAND | wx.ALL, 5)
       
        PalettesSizer = wx.BoxSizer(wx.HORIZONTAL)
        PalettePanelSizer.Add(PalettesSizer, 0, wx.EXPAND | wx.ALL, 5)
        
        hbox_high = wx.BoxSizer(wx.VERTICAL)
        hbox_low = wx.BoxSizer(wx.VERTICAL)
        PalettesSizer.Add(hbox_high, 0, wx.EXPAND | wx.ALL, 5)
        PalettesSizer.Add(hbox_low, 0, wx.EXPAND | wx.ALL, 5)
        
        ln = wx.StaticLine(PalettePanel, -1, style=wx.LI_VERTICAL)
        ln.SetSize((2,200))
        PalettesSizer.Add(ln, 0, wx.EXPAND | wx.ALL, 5)
        
        hbox_high2 = wx.BoxSizer(wx.VERTICAL)
        hbox_low2 = wx.BoxSizer(wx.VERTICAL)
        PalettesSizer.Add(hbox_high2, 0, wx.EXPAND | wx.ALL, 5)
        PalettesSizer.Add(hbox_low2, 0, wx.EXPAND | wx.ALL, 5)
        self.ColorButtons = []
        btnSize = ((55, 24)) 
        for n in range(32):
            button = Button(PalettePanel, n, "", size=btnSize)
            self.Bind(wx.EVT_BUTTON, self.edit_color, id=n)
            if n < 8:
                hbox_high.Add(button, 0, wx.EXPAND | wx.ALL, 2)
            elif n > 7 and n < 16:
                hbox_low.Add(button, 0, wx.EXPAND | wx.ALL, 2)
            elif n > 15 and n < 24:
                hbox_high2.Add(button, 0, wx.EXPAND | wx.ALL, 2)
            else:
                hbox_low2.Add(button, 0, wx.EXPAND | wx.ALL, 2)
            self.ColorButtons.append(button)
        
        PositionPanel = wx.Panel(self, -1, style=wx.RAISED_BORDER|wx.TAB_TRAVERSAL)
        PositionPanelSizer = wx.BoxSizer(wx.VERTICAL)
        PositionPanel.SetSizer(PositionPanelSizer)
        self.sizer.Add(PositionPanel, 0, wx.EXPAND | wx.ALL, 5)
        
        PositionEntrySizer = wx.GridBagSizer(3,3)
        PositionPanelSizer.Add(PositionEntrySizer, 0, wx.EXPAND | wx.ALL, 5)
        
        PlayerY_txt = wx.StaticText(PositionPanel, -1,"Player Y:")
        PositionEntrySizer.Add(PlayerY_txt, (0, 0), wx.DefaultSpan,  wx.ALL, 6)
        self.PlayerY = wx.SpinCtrl(PositionPanel, -1,style=wx.TE_CENTRE, size=(60,-1))
        self.PlayerY.SetRange(0,127)
        PositionEntrySizer.Add(self.PlayerY,(0, 1), wx.DefaultSpan,  wx.ALL, 4)
        
        EnemyY_txt = wx.StaticText(PositionPanel, -1,"Enemy Y:")
        PositionEntrySizer.Add(EnemyY_txt, (1, 0), wx.DefaultSpan,  wx.ALL, 6)
        self.EnemyY = wx.SpinCtrl(PositionPanel, -1,style=wx.TE_CENTRE, size=(60,-1))
        self.EnemyY.SetRange(0,127)
        PositionEntrySizer.Add(self.EnemyY,(1, 1), wx.DefaultSpan,  wx.ALL, 4)
        
        EnemyAlt_txt = wx.StaticText(PositionPanel, -1,"Enemy Altitude:")
        PositionEntrySizer.Add(EnemyAlt_txt, (2, 0), wx.DefaultSpan,  wx.ALL, 6)
        self.EnemyAlt = wx.SpinCtrl(PositionPanel, -1,style=wx.TE_CENTRE, size=(60,-1))
        self.EnemyAlt.SetRange(0,127)
        PositionEntrySizer.Add(self.EnemyAlt,(2, 1), wx.DefaultSpan,  wx.ALL, 4)
        
        GUIEditor = Button(PositionPanel, 55, "Graphic Position Editor")
        self.Bind(wx.EVT_BUTTON, self.PositionEditor, id=55)
        PositionPanelSizer.Add(GUIEditor, 0, wx.EXPAND | wx.ALL, 2)
        
        IconPanel = wx.Panel(self, -1, style=wx.RAISED_BORDER|wx.TAB_TRAVERSAL)
        IconPanelSizer = wx.BoxSizer(wx.VERTICAL)
        IconPanel.SetSizer(IconPanelSizer)
        self.sizer.Add(IconPanel, 0, wx.EXPAND | wx.ALL, 5)
        
        IconImageSizer = wx.BoxSizer(wx.HORIZONTAL)
        IconPanelSizer.Add(IconImageSizer, 0, wx.EXPAND | wx.ALL, 0)
        
        self.Icons = wx.BitmapButton(IconPanel,61,wx.EmptyBitmap(32,64), size=(44,76))
        self.Icons.SetCursor(wx.StockCursor(wx.CURSOR_HAND))
        self.Bind(wx.EVT_BUTTON, self.LoadIcon, id=61)
        IconImageSizer.Add(self.Icons, 0, wx.EXPAND | wx.ALL, 5)
        
        self.AniIcon = wx.BitmapButton(IconPanel,62,wx.EmptyBitmap(64,64), size=(76,76))
        self.Bind(wx.EVT_BUTTON, self.LoadIcon, id=62)
        self.AniIcon.SetCursor(wx.StockCursor(wx.CURSOR_HAND))
        IconImageSizer.Add(self.AniIcon, 0, wx.EXPAND | wx.ALL, 5)
        
        IconRepoint = Button(IconPanel, 55, "Repoint Icon")
        self.Bind(wx.EVT_BUTTON, self.RepointIcon, id=65)
        IconPanelSizer.Add(IconRepoint, 0, wx.EXPAND | wx.ALL, 5)
        
        self.IconPalChoice = wx.ComboBox(IconPanel, -1, choices=[],
                                            style=wx.SUNKEN_BORDER, size=(60, -1))
        self.IconPalChoice.Bind(wx.EVT_COMBOBOX, self.SwapIconPal)
        IconPanelSizer.Add(self.IconPalChoice, 0, wx.EXPAND | wx.ALL, 5)
        
        
        IconPalBox = wx.BoxSizer(wx.HORIZONTAL)
        IconPanelSizer.Add(IconPalBox, 0, wx.EXPAND | wx.ALL, 0)
        
        IconPalBoxLeft = wx.BoxSizer(wx.VERTICAL)
        IconPalBox.Add(IconPalBoxLeft, 0, wx.EXPAND | wx.ALL, 0)
        IconPalBoxRight = wx.BoxSizer(wx.VERTICAL)
        IconPalBox.Add(IconPalBoxRight, 0, wx.EXPAND | wx.ALL, 0)
        self.IconColorButtons = []
        IconButtonsize = (60,21)
        for n in range(16):
            #Use IDs 70->86
            ID = 70
            button = Button(IconPanel, 70+n, "", size=IconButtonsize)
            self.Bind(wx.EVT_BUTTON, self.editIconColor, id=70+n)
            if n < 8:
                IconPalBoxLeft.Add(button, 0, wx.EXPAND | wx.ALL, 5)
            elif n > 7:
                IconPalBoxRight.Add(button, 0, wx.EXPAND | wx.ALL, 5)
            self.IconColorButtons.append(button)
        
        self.load_everything(self.poke_num)
    
    def RepointIcon(self):
        repointer = SpriteRepointer(self.rom_name, 
                                                need=len(GBAFSLZ), 
                                                repoint_what="Icon")
        if repointer.ShowModal() == wx.ID_OK:
            iconspritetable = int(self.config.get(self.rom_id, "iconspritetable"), 0)
            rom.seek(iconspritetable+(self.poke_num+1)*4)
            #Write new pointer
            offset = repointer.offset
            hexOffset = hex(offset+0x8000000).rstrip("L").lstrip("0x").zfill(8)
            hexOffset = make_pointer(hexOffset)
            hexOffset = unhexlify(hexOffset)
            rom.write(hexOffset)
            #Write new image
            rom.seek(offset)
            rom.write(self.GBAIcon)
            self.IconPointer = offset
        else:
            ERROR = wx.MessageDialog(None, 
                                "Either no offset was selected or you aborted repoint. Nothing was changed.", 
                                'Just letting you know...', 
                                wx.OK | wx.ICON_ERROR)
            ERROR.ShowModal()
            
    def save(self):
        #Save sprites
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
        numiconpalettes = int(self.config.get(self.rom_id, "numiconpalettes"), 0)
        
        bytes_per_entry = 8 ##Need to load from ini for EMERALD
        overwrite = self.cb.IsChecked()
        with open(self.rom_name, "r+b") as rom:
            if self.Changes["front"] != False:
                GBAFSLZ = LZCompress(self.GBAFrontSprite)
                if len(GBAFSLZ) > self.OrgSizes["front"]:
                    repointer = SpriteRepointer(self.rom_name, 
                                                             need=len(GBAFSLZ), 
                                                             repoint_what="Front Sprite")
                    while True:
                        if repointer.ShowModal() == wx.ID_OK:
                            if repointer.offset == self.FrontSpritePointer: continue
                            elif repointer.offset == None: continue
                            else:
                                rom.seek(FrontSpriteTable+(self.poke_num)*bytes_per_entry)
                                #Write new pointer
                                offset = repointer.offset
                                hexOffset = hex(offset+0x8000000).rstrip("L").lstrip("0x").zfill(8)
                                hexOffset = make_pointer(hexOffset)
                                hexOffset = unhexlify(hexOffset)
                                rom.write(hexOffset)
                                #Clear old image
                                if overwrite == True:
                                    rom.seek(self.FrontSpritePointer)
                                    
                                    for x in range(self.OrgSizes["front"]):
                                        rom.write("\xFF")
                                #Write new image
                                rom.seek(offset)
                                rom.write(GBAFSLZ)
                                self.OrgSizes["front"] = len(GBAFSLZ)
                                break
                else:
                    rom.seek(self.FrontSpritePointer)
                    rom.write(GBAFSLZ)
                                
            if self.Changes["back"] != False:
                GBABSLZ = LZCompress(self.GBABackSprite)
                if len(GBABSLZ) > self.OrgSizes["back"]:
                    repointer = SpriteRepointer(self.rom_name, 
                                                             need=len(GBABSLZ), 
                                                             repoint_what="Back Sprite")
                    while True:
                        if repointer.ShowModal() == wx.ID_OK:
                            
                            if repointer.offset == self.BackSpritePointer: continue
                            elif repointer.offset == None: continue
                            else:
                                rom.seek(BackSpriteTable+(self.poke_num)*bytes_per_entry)
                                #Write new pointer
                                offset = repointer.offset
                                hexOffset = hex(offset+0x8000000).rstrip("L").lstrip("0x").zfill(8)
                                hexOffset = make_pointer(hexOffset)
                                hexOffset = unhexlify(hexOffset)
                                rom.write(hexOffset)
                                #Clear old image
                                if overwrite == True:
                                    rom.seek(self.BackSpritePointer)
                                    for x in range(self.OrgSizes["back"]):
                                        rom.write("\xFF")
                                #Write new image
                                rom.seek(offset)
                                rom.write(GBABSLZ)
                                self.OrgSizes["back"] = len(GBABSLZ)
                                break
                else:
                    rom.seek(self.BackSpritePointer)
                    rom.write(GBABSLZ)
                    
            if self.Changes["normal"] != False:
                normal = Convert25bitPalettetoGBA(self.FrontPalette)
                GBANORMALLZ = LZCompress(normal)
                if len(GBANORMALLZ) > self.OrgSizes["normal"]:
                    repointer = SpriteRepointer(self.rom_name, 
                                                             need=len(GBANORMALLZ), 
                                                             repoint_what="Normal Palette")
                    while True:
                        if repointer.ShowModal() == wx.ID_OK:
                            
                            if repointer.offset == self.FrontPalettePointer: continue
                            elif repointer.offset == None: continue
                            else:
                                rom.seek(FrontPaletteTable+(self.poke_num)*bytes_per_entry)
                                #Write new pointer
                                offset = repointer.offset
                                hexOffset = hex(offset+0x8000000).rstrip("L").lstrip("0x").zfill(8)
                                hexOffset = make_pointer(hexOffset)
                                hexOffset = unhexlify(hexOffset)
                                rom.write(hexOffset)
                                if overwrite == True:
                                #Clear old image
                                    rom.seek(self.FrontPalettePointer)
                                    for x in range(self.OrgSizes["normal"]):
                                        rom.write("\xFF")
                                #Write new image
                                rom.seek(offset)
                                rom.write(GBANORMALLZ)
                                self.OrgSizes["normal"] = len(GBANORMALLZ)
                                break
                else:
                    rom.seek(self.FrontPalettePointer)
                    rom.write(GBANORMALLZ)
                    
            if self.Changes["shiny"] != False:
                shiny = Convert25bitPalettetoGBA(self.ShinyPalette)
                GBASHINYLZ = LZCompress(shiny)
                if len(GBASHINYLZ) > self.OrgSizes["shiny"]:
                    repointer = SpriteRepointer(self.rom_name, 
                                                             need=len(GBASHINYLZ), 
                                                             repoint_what="Shiny Palette")
                    while True:
                        if repointer.ShowModal() == wx.ID_OK:
                            
                            if repointer.offset == self.ShinyPalettePointer: continue
                            elif repointer.offset == None: continue
                            else:
                                rom.seek(ShinyPaletteTable+(self.poke_num)*bytes_per_entry)
                                #Write new pointer
                                offset = repointer.offset
                                hexOffset = hex(offset+0x8000000).rstrip("L").lstrip("0x").zfill(8)
                                hexOffset = make_pointer(hexOffset)
                                hexOffset = unhexlify(hexOffset)
                                rom.write(hexOffset)
                                #Clear old image
                                if overwrite == True:
                                    rom.seek(self.ShinyPalettePointer)
                                    for x in range(self.OrgSizes["shiny"]):
                                        rom.write("\xFF")
                                #Write new image
                                rom.seek(offset)
                                rom.write(GBASHINYLZ)
                                self.OrgSizes["shiny"] = len(GBASHINYLZ)
                                break
                else:
                    rom.seek(self.ShinyPalettePointer)
                    rom.write(GBASHINYLZ)
            #Write positions
            rom.seek(playerytable+(self.poke_num)*4+1)
            PlayerY = hex(self.PlayerY.GetValue()).rstrip("L").lstrip("0x").zfill(2)
            rom.write(unhexlify(PlayerY))
            
            rom.seek(enemyaltitudetable+(self.poke_num)*4+1)
            EnemyAlt = hex(self.EnemyAlt.GetValue()).rstrip("L").lstrip("0x").zfill(2)
            rom.write(unhexlify(EnemyAlt))
            
            rom.seek(enemyytable+(self.poke_num)*4+1)
            EnemyY = hex(self.EnemyY.GetValue()).rstrip("L").lstrip("0x").zfill(2)
            rom.write(unhexlify(EnemyY))
            
            #Write all things Icon
            rom.seek(self.IconPointer)
            rom.write(self.GBAIcon)
            
            pals = ""
            for pal in self.IconPals:
                tmp = Convert25bitPalettetoGBA(pal)
                pals += tmp
            rom.seek(iconpalettes)
            rom.write(pals)
            
    def SwapIconPal(self, instance):
        self.IconPalNum = instance.GetSelection()
        self.ReloadShownSprites()
        
    def editIconColor(self, instance):
        instance = instance.GetEventObject()
        color_number = instance.Id-70
        dlg = wx.ColourDialog(self)
        dlg.GetColourData().SetChooseFull(True)
        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.GetColourData()
        else: return
        dlg.Destroy()
        self.IconPals[self.IconPalNum][color_number] = data.GetColour()
        self.ReloadShownSprites()
    
    def edit_color(self, instance):
        instance = instance.GetEventObject()
        color_number = instance.Id
        dlg = wx.ColourDialog(self)
        dlg.GetColourData().SetChooseFull(True)
        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.GetColourData()
        else: return
        dlg.Destroy()
        if color_number < 16:
            self.FrontPalette[color_number] = data.GetColour()
            self.Changes["normal"]=True
        else:
            self.ShinyPalette[color_number-16] = data.GetColour()
            self.Changes["shiny"]=True
        self.ReloadShownSprites()
    
    def LoadIcon(self, instance):
        open_dialog = wx.FileDialog(self, message="Open an icon...", 
                                                        defaultDir=self.lastPath, style=wx.OPEN)
        if open_dialog.ShowModal() == wx.ID_OK:
            filename = open_dialog.GetPath()
            self.lastPath = os.path.dirname(filename)
            raw = Image.open(filename)
            if raw.size != (32,64):
                raise AttributeError("Image is "+raw.size[0]+"x"+raw.size[1]+". It must be 32x64.")
            if raw.mode != "P":
                converted = raw.convert("P", palette=Image.ADAPTIVE, colors=16)
            else:
                if len(raw.getcolors()) > 16:
                    tmp = raw.convert("RGB")
                    converted = raw.convert("P", palette=Image.ADAPTIVE, colors=16)
                else: converted = raw
            converted = converted.convert("RGB")
            
            TC = self.IconPals[self.IconPalNum][0]
            TransColor = (TC[0],TC[1],TC[2])
            
            PILPal = []
            for color in self.IconPals[self.IconPalNum]:
                PILPal.append(color[0])
                PILPal.append(color[1])
                PILPal.append(color[2])
            while len(PILPal) < 256*3:
                PILPal.append(TC[0])
                PILPal.append(TC[1])
                PILPal.append(TC[2])
            PILImg = Image.new("P", (64, 64), 0)
            PILImg.putpalette(PILPal)
            
            pixels = converted.load()
            FirstColor = pixels[0,0]
            for y in range(64):
                for x in range(32):
                    if pixels[x,y] == FirstColor:
                        pixels[x,y] = TransColor
            converted = converted.quantize(palette=PILImg)
            converted = converted.convert("RGB")
            
            image = PilImageToWxImage(converted)
            self.GBAIcon, palette = ConvertNormalImageToGBA(image, palette=self.IconPals[self.IconPalNum], size=(32,64))
            self.TMPIcon = ConvertGBAImageToNormal(self.GBAIcon,self.IconPals[self.IconPalNum],size=(32,64))
            self.Icons.SetBitmapLabel(self.TMPIcon)
            self.ReloadShownSprites()
    
    def ReloadShownSprites(self):
        self.TMPFrontSprite = ConvertGBAImageToNormal(self.GBAFrontSprite,self.FrontPalette)
        self.TMPBackSprite = ConvertGBAImageToNormal(self.GBABackSprite,self.FrontPalette)
        self.TMPSFrontSprite = ConvertGBAImageToNormal(self.GBAFrontSprite,self.ShinyPalette)
        self.TMPSBackSprite = ConvertGBAImageToNormal(self.GBABackSprite,self.ShinyPalette)
        
        self.FrontSprite.SetBitmapLabel(self.TMPFrontSprite)
        self.BackSprite.SetBitmapLabel(self.TMPBackSprite)
        self.SFrontSprite.SetBitmapLabel(self.TMPSFrontSprite)
        self.SBackSprite.SetBitmapLabel(self.TMPSBackSprite)
        
        self.TMPIcon = ConvertGBAImageToNormal(self.GBAIcon,self.IconPals[self.IconPalNum],size=(32,64))
        self.Icons.SetBitmapLabel(self.TMPIcon)
        
        for num, color in enumerate(self.FrontPalette):
            self.ColorButtons[num].SetBackgroundColour(color)
        for num, color in enumerate(self.ShinyPalette):
            self.ColorButtons[num+16].SetBackgroundColour(color)
        for num, color in enumerate(self.IconPals[self.IconPalNum]):
            self.IconColorButtons[num].SetBackgroundColour(color)
            
        tmpimage = wx.ImageFromBitmap(self.TMPIcon)
            
        self.IconTop = tmpimage.GetSubImage((0,0,32,32)).Scale(64, 64)
        self.IconBottom = tmpimage.GetSubImage((0,32,32,32)).Scale(64, 64)
        
        self.IconTop = wx.BitmapFromImage(self.IconTop)
        self.IconBottom = wx.BitmapFromImage(self.IconBottom)
    
    def LoadSingleSprite(self, instance):
        open_dialog = wx.FileDialog(self, message="Open a sprite...", 
                                                        defaultDir=self.lastPath, style=wx.OPEN)
        if open_dialog.ShowModal() == wx.ID_OK:
            filename = open_dialog.GetPath()
            self.lastPath = os.path.dirname(filename)
            raw = Image.open(filename)
            if raw.size != (64,64):
                raise AttributeError("Image is "+raw.size[0]+"x"+raw.size[1]+". It must be 64x64.")
            if raw.mode != "P":
                converted = raw.convert("P", palette=Image.ADAPTIVE, colors=16)
            else:
                if len(raw.getcolors()) > 16:
                    tmp = raw.convert("RGB")
                    converted = raw.convert("P", palette=Image.ADAPTIVE, colors=16)
                else: converted = raw
            image = PilImageToWxImage(converted)
            gbaversion, palette = ConvertNormalImageToGBA(image)
            
            instance = instance.GetEventObject()
            sprite_number = instance.Id
            
            if sprite_number == 56:
                self.GBAFrontSprite = gbaversion
                self.FrontPalette = palette
                self.Changes["front"]=True
                self.Changes["normal"]=True
            elif sprite_number == 57:
                self.GBABackSprite = gbaversion
                self.FrontPalette = palette
                self.Changes["back"]=True
                self.Changes["normal"]=True
            elif sprite_number == 58:
                self.GBAFrontSprite = gbaversion
                self.ShinyPalette = palette
                self.Changes["front"]=True
                self.Changes["shiny"]=True
            elif sprite_number == 59:
                self.GBABackSprite = gbaversion
                self.ShinyPalette = palette
                self.Changes["back"]=True
                self.Changes["shiny"]=True
            self.ReloadShownSprites()
            
    def LoadSheetSprite(self, instance):
        open_dialog = wx.FileDialog(self, message="Open a sprite sheet...", 
                                                        defaultDir=self.lastPath, style=wx.OPEN)
        if open_dialog.ShowModal() == wx.ID_OK:
            filename = open_dialog.GetPath()
            self.lastPath = os.path.dirname(filename)
            raw = Image.open(filename)
            if raw.size != (256,64):
                raise AttributeError("Image is "+raw.size[0]+"x"+raw.size[1]+". It must be 256x64.")
            front = raw.copy().crop((0, 0, 64, 64))
            shiny = raw.copy().crop((64, 0, 128, 64))
            back = raw.copy().crop((128, 0, 192, 64))
            frontback = Image.new("RGB", (128,64))
            frontback.paste(front, (0,0))
            frontback.paste(back, (64,0))
            if frontback.mode != "P":
                frontback = frontback.convert("P", palette=Image.ADAPTIVE, colors=16)
            else:
                if len(frontback.getcolors()) > 16:
                    tmp = frontback.convert("RGB")
                    frontback = tmp.convert("P", palette=Image.ADAPTIVE, colors=16)
            if shiny.mode != "P":
                shiny = shiny.convert("P", palette=Image.ADAPTIVE, colors=16)
            else:
                if len(shiny.getcolors()) > 16:
                    tmp = shiny.convert("RGB")
                    shiny = tmp.convert("P", palette=Image.ADAPTIVE, colors=16)
            front = frontback.copy().crop((0, 0, 64, 64))
            back = frontback.copy().crop((64, 0, 128, 64))
            wxfront = PilImageToWxImage(front)
            self.GBAFrontSprite, self.FrontPalette = ConvertNormalImageToGBA(wxfront)
            wxback = PilImageToWxImage(back)
            self.GBABackSprite, tmp = ConvertNormalImageToGBAUnderPal(wxback, self.FrontPalette)
            self.ShinyPalette = GetShinyPalette(front.convert("RGB"), shiny.convert("RGB"), self.FrontPalette)
            self.ReloadShownSprites()
            self.Changes["front"]=True
            self.Changes["back"]=True
            self.Changes["normal"]=True
            self.Changes["shiny"]=True
            
    def load_everything(self, poke_num):
        self.Changes = {"front":False, "back":False, "normal":False, "shiny":False}
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
        numiconpalettes = int(self.config.get(self.rom_id, "numiconpalettes"), 0)
        
        bytes_per_entry = 8 ##Need to load from ini for EMERALD
        
        with open(self.rom_name, "r+b") as rom:
            rom.seek(FrontSpriteTable+(poke_num)*bytes_per_entry)
            self.FrontSpritePointer = read_pointer(rom.read(4))
            rom.seek(BackSpriteTable+(poke_num)*bytes_per_entry)
            self.BackSpritePointer = read_pointer(rom.read(4))
            rom.seek(FrontPaletteTable+(poke_num)*bytes_per_entry)
            self.FrontPalettePointer = read_pointer(rom.read(4))
            rom.seek(ShinyPaletteTable+(poke_num)*bytes_per_entry)
            self.ShinyPalettePointer = read_pointer(rom.read(4))
        
            self.GBAFrontSprite, self.OrgSizes["front"] = LZUncompress(rom, self.FrontSpritePointer, True)
            self.GBABackSprite, self.OrgSizes["back"] = LZUncompress(rom, self.BackSpritePointer, True)
            FrontPalette, self.OrgSizes["normal"] = LZUncompress(rom, self.FrontPalettePointer, True)
            ShinyPalette, self.OrgSizes["shiny"] = LZUncompress(rom, self.ShinyPalettePointer, True)
            
            self.FrontPalette = ConvertGBAPalTo25Bit(FrontPalette)
            self.ShinyPalette = ConvertGBAPalTo25Bit(ShinyPalette)
            
            self.TMPFrontSprite = ConvertGBAImageToNormal(self.GBAFrontSprite,self.FrontPalette)
            self.TMPBackSprite = ConvertGBAImageToNormal(self.GBABackSprite,self.FrontPalette)
            self.TMPSFrontSprite = ConvertGBAImageToNormal(self.GBAFrontSprite,self.ShinyPalette)
            self.TMPSBackSprite = ConvertGBAImageToNormal(self.GBABackSprite,self.ShinyPalette)
            self.Refresh()
            
            self.FrontSprite.SetBitmapLabel(self.TMPFrontSprite)
            self.BackSprite.SetBitmapLabel(self.TMPBackSprite)
            self.SFrontSprite.SetBitmapLabel(self.TMPSFrontSprite)
            self.SBackSprite.SetBitmapLabel(self.TMPSBackSprite)
            
            rom.seek(playerytable+(poke_num)*4+1)
            PlayerY = deal_with_8bit_signed_hex(int(get_bytes_string_from_hex_string(rom.read(1)),16))
            self.PlayerY.SetValue(PlayerY)
            
            rom.seek(enemyaltitudetable+(poke_num))
            EnemyAlt = deal_with_8bit_signed_hex(int(get_bytes_string_from_hex_string(rom.read(1)),16))
            self.EnemyAlt.SetValue(EnemyAlt)
            
            rom.seek(enemyytable+(poke_num)*4+1)
            EnemyY = deal_with_8bit_signed_hex(int(get_bytes_string_from_hex_string(rom.read(1)),16))
            self.EnemyY.SetValue(EnemyY)
            
            rom.seek(iconspritetable+(poke_num)*4)
            self.IconPointer = read_pointer(rom.read(4))
            rom.seek(self.IconPointer)
            self.GBAIcon = rom.read((32*64)/2)
            
            rom.seek(iconpalettetable+(poke_num))
            self.IconPalNum = int(hexlify(rom.read(1)),16)
            
            rom.seek(iconpalettes)
            self.IconPals = []
            for n in range(numiconpalettes):
                self.IconPals.append(ConvertGBAPalTo25Bit(rom.read(32)))
               
            self.TMPIcon = ConvertGBAImageToNormal(self.GBAIcon,self.IconPals[self.IconPalNum],size=(32,64))
            self.Icons.SetBitmapLabel(self.TMPIcon)
            
            tmpimage = wx.ImageFromBitmap(self.TMPIcon)
            
            self.IconTop = tmpimage.GetSubImage((0,0,32,32)).Scale(64, 64)
            self.IconBottom = tmpimage.GetSubImage((0,32,32,32)).Scale(64, 64)
            
            self.IconTop = wx.BitmapFromImage(self.IconTop)
            self.IconBottom = wx.BitmapFromImage(self.IconBottom)
            
            self.AniIcon.SetBitmapLabel(self.IconTop)
            self.SetIconTimer(1)
            
        for num, color in enumerate(self.FrontPalette):
            self.ColorButtons[num].SetBackgroundColour(color)
        for num, color in enumerate(self.ShinyPalette):
            self.ColorButtons[num+16].SetBackgroundColour(color)
        for num, color in enumerate(self.IconPals[self.IconPalNum]):
            self.IconColorButtons[num].SetBackgroundColour(color)
        nums = []
        for n in range(numiconpalettes):
            nums.append(str(n))
        self.IconPalChoice.Clear()
        self.IconPalChoice.AppendItems(nums) 
        self.IconPalChoice.SetSelection(self.IconPalNum)
            
    def OnIconTimer1(self, event):
        self.SetIconTimer(2)
        self.AniIcon.SetBitmapLabel(self.IconTop)
        
    def OnIconTimer2(self, event):
        self.SetIconTimer(1)
        self.AniIcon.SetBitmapLabel(self.IconBottom)
        
    def SetIconTimer(self, num):
        TIMER_ID = 2  # pick a number
        self.Icontimer = wx.Timer(self, TIMER_ID)  # message will be sent to the panel
        self.Icontimer.Start(250)  # 100 milliseconds
        if num == 1:
            wx.EVT_TIMER(self, TIMER_ID, self.OnIconTimer1)  # call the on_timer function
        elif num == 2:
            wx.EVT_TIMER(self, TIMER_ID, self.OnIconTimer2)
        
    def PositionEditor(self, instance):
        #origin for pokeback is (40,48)
        #origin for pokefront is (144,8)
        pygame.init()
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
        
        alt = self.EnemyAlt.GetValue()
        
        self.shadow = pygame.image.load(os.path.join("Resources","Shadow.png"))
        self.shadow_rect = pygame.Rect(160,65,32,8)
        FrontHeight = 8+self.EnemyY.GetValue()-alt
        PokeFrontRect = pygame.Rect(144,FrontHeight,64,64)
        
        self.PYGPokeBack = pygame.image.load(os.path.join("Resources","PokeBack.png"))
        transparent_color = self.PYGPokeBack.get_at((0,0))
        self.PYGPokeBack.set_colorkey(transparent_color)
        
        BackHeight = 48+self.PlayerY.GetValue()
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
        self.timer.Start(100)  # 100 milliseconds
        wx.EVT_TIMER(self, TIMER_ID, self.on_timer)  # call the on_timer function
        
    def PositionEditorLoop(self, *args):
        need_update = []
        pygame.event.pump()
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    self.timer.Stop()
        for map in self.Mappings:
            if keys[map[0]]:
                need_update.append(map[1])
        for need in need_update:
            if need == "PUp":
                try:
                    curr = self.PlayerY.GetValue()
                    curr -= 1
                    self.PlayerY.SetValue(curr)
                except: pass
            elif need == "PDown":
                try:
                    curr = self.PlayerY.GetValue()
                    curr += 1
                    self.PlayerY.SetValue(curr)
                except: pass
            elif need == "EUp":
                try:
                    curr = self.EnemyY.GetValue()
                    curr -= 1
                    self.EnemyY.SetValue(curr)
                except: pass
            elif need == "EDown":
                try:
                    curr = self.EnemyY.GetValue()
                    curr += 1
                    self.EnemyY.SetValue(curr)
                except: pass
            elif need == "EAUp":
                try:
                    curr = self.EnemyAlt.GetValue()
                    curr += 1
                    self.EnemyAlt.SetValue(curr)
                except: pass
            elif need == "EADown":
                try:
                    curr = self.EnemyAlt.GetValue()
                    curr -= 1
                    self.EnemyAlt.SetValue(curr)
                except: pass
            
        self.UpdatePosition()
                
    def UpdatePosition(self):
        try:
            alt = self.EnemyAlt.GetValue()
            FrontHeight = 8+self.EnemyY.GetValue()-alt
            PokeFrontRect = pygame.Rect(144,FrontHeight,64,64)
            
            BackHeight = 48+self.PlayerY.GetValue()
            PokeBackRect = pygame.Rect(40,BackHeight,64,64)
            
            self.screen.blit(self.PYGBG,pygame.Rect(0,0,240,160))
            if alt > 0:
                self.screen.blit(self.shadow,self.shadow_rect)
            self.screen.blit(self.PYGPokeFront,PokeFrontRect)
            self.screen.blit(self.PYGPokeBack,PokeBackRect)
            self.screen.blit(self.PYGTEXTBOX,pygame.Rect(0,0,240,160))
            pygame.display.flip()
        except: pass
        
class SpriteRepointer(wx.Dialog):
    def __init__(self, rom, parent=None, need=None, repoint_what=None, *args, **kw):
        wx.Dialog.__init__(self, parent=parent, id=wx.ID_ANY)
        self.SetWindowStyle( self.GetWindowStyle() | wx.STAY_ON_TOP | wx.RESIZE_BORDER )
        
        self.offset = None
        self.num = need
        self.repoint = repoint_what
        self.rom = rom
        self.InitUI()
        self.OnSearch()
        self.SetTitle("Repoint "+self.repoint)
        
    def InitUI(self):
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        txt = wx.StaticText(self, -1, self.repoint+" needs to be repointed.\n\n",style=wx.TE_CENTRE)
        vbox.Add(txt, 0, wx.EXPAND | wx.ALL, 5)
        
        txt2 = wx.StaticText(self, -1, "Please choose an offset to repoint to or specify\na manual offset. If a manual offset is specified,\nthe list choice will be ignored.\nNOTE: Manual offsets will NOT be checked for\nfree space availability.",style=wx.TE_CENTRE)
        vbox.Add(txt2, 0, wx.EXPAND | wx.ALL, 5)
        
        self.OFFSETS = wx.ListBox(self, -1)
        self.OFFSETS.Bind(wx.EVT_LISTBOX, self.GetOffset)
        vbox.Add(self.OFFSETS, 0, wx.EXPAND | wx.ALL, 5)
        
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        manual_txt = wx.StaticText(self, -1, "Manual Offset: 0x",style=wx.TE_CENTRE)
        hbox.Add(manual_txt, 0, wx.EXPAND | wx.LEFT|wx.TOP|wx.BOTTOM, 5)
        self.MANUAL = wx.TextCtrl(self, -1,style=wx.TE_CENTRE, size=(100,-1))
        self.MANUAL.Bind(wx.EVT_TEXT, self.GetOffset)
        hbox.Add(self.MANUAL, 0, wx.EXPAND | wx.RIGHT|wx.TOP|wx.BOTTOM, 5)
        vbox.Add(hbox, 0, wx.EXPAND | wx.ALL, 0)
        
        OK = self.CreateButtonSizer(wx.OK)
        vbox.Add(OK, 0, wx.EXPAND | wx.ALL, 5)
        
        txt3 = wx.StaticText(self, -1, "______________________________",style=wx.TE_CENTRE)
        vbox.Add(txt3, 0, wx.EXPAND | wx.ALL, 15)
        
        self.SetSizerAndFit(vbox)
        self.Fit()
        self.SetMinSize(self.GetEffectiveMinSize())
        
    def GetOffset(self, *args):
        sel = self.OFFSETS.GetSelection()
        _offset_ = self.MANUAL.GetValue()
        
        if _offset_ != "":
            if len(_offset_) > 6:
                check = _offset_[-7:-6]
                if check == "1" or check == "9":
                    check = "1"
                else:
                    check = ""
                _offset_ = check+_offset_[-6:].zfill(6)
        elif sel != -1:
            _offset_ = self.OFFSETS.GetString(sel)[2:]
        else: return
        
        try: self.offset = int(_offset_, 16)
        except: return

    def OnSearch(self, *args):
        self.OFFSETS.Clear()
        search = "\xff"*self.num
        with open(self.rom, "r+b") as rom:
            rom.seek(0)
            read = rom.read()
            x = (0,True)
            start = 7602176
            for n in range(5):
                if x[1] == None:
                    break
                x = (0,True)
                while x[0] != 1:
                    offset = read.find(search, start)
                    if offset == -1:
                        x = (1,None)
                    if offset%4 != 0:
                        start = offset+1
                        continue
                    if read[offset-1] != "\xFF":
                        start = offset+1
                        continue
                    self.OFFSETS.Append(hex(offset))
                    x = (1,True)
                    start = offset+len(search)