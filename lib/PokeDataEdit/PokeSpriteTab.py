from lib.Tools.LZ77 import *
from binascii import hexlify, unhexlify
from lib.Tools.ImageFunctions import *
from lib.Tools.rom_insertion_operations import *
import os,time,textwrap
from PIL import Image
from lib.Tools.PILandWXPythonConversions import *
from lib.OverLoad.Button import *
from lib.PokeDataEdit.PosEditor import *
from lib.Tools.Recovery import *

class SpriteTab(wx.Panel):
    def __init__(self, parent, rom=None, config=None, rom_id=None):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        self.rom_name = rom
        self.NoLoad = False
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
        
        self.LoadAllButton = Button(spritePanel, 60, "Load 256x64 Sheet")
        self.Bind(wx.EVT_BUTTON, self.LoadSheetSprite, id=60)
        SpritesAndPals.Add(self.LoadAllButton, 0, wx.EXPAND | wx.ALL, 6)
        
        self.cb = wx.CheckBox(spritePanel, -1, 'Fill sprites with 0xFF on repoint?', (10, 10))
        self.cb.SetValue(False)
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
        
        FrameHBox = wx.BoxSizer(wx.HORIZONTAL)
        PositionPanelSizer.Add(FrameHBox, 0, wx.EXPAND | wx.ALL, 5)
        
        Frame_txt = wx.StaticText(PositionPanel, -1,"Sprite Frame:")
        FrameHBox.Add(Frame_txt, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5)
        self.Frames = wx.SpinCtrl(PositionPanel, -1,style=wx.TE_CENTRE, size=(100,-1))
        self.Frames.Bind(wx.EVT_TEXT, self.ReloadShownSprites)
        FrameHBox.Add(self.Frames, 0, wx.EXPAND | wx.ALL, 5)
        
        self.SeperateFrames = wx.CheckBox(PositionPanel, -1, 'Repoint Frames Seperately?', (10, 10))
        self.SeperateFrames.SetValue(False)
        PositionPanelSizer.Add(self.SeperateFrames, 0, wx.ALL|wx.ALIGN_CENTER, 5)
        
        ChangePointers = Button(PositionPanel, 66, "Change Pointers for Images")
        self.Bind(wx.EVT_BUTTON, self.OnChangePointers, id=66)
        PositionPanelSizer.Add(ChangePointers, 0, wx.ALL|wx.ALIGN_CENTER, 5)
        
        lnH = wx.StaticLine(PositionPanel, -1, style=wx.LI_HORIZONTAL)
        lnH.SetSize((2,200))
        PositionPanelSizer.Add(lnH, 0, wx.EXPAND | wx.ALL, 10)
        
        PositionEditorPanel = wx.Panel(PositionPanel,size=(244,164), style=wx.RAISED_BORDER|wx.TAB_TRAVERSAL)
        self.PosEdit = PosEditorBase(PositionEditorPanel)
        PositionPanelSizer.Add(PositionEditorPanel, 0, wx.EXPAND | wx.ALL, 5)
        PositionEditorPanel.Bind(wx.EVT_PAINT, self.PosEdit.OnPaint)
        
        PositionEntrySizer = wx.GridBagSizer(3,3)
        PositionPanelSizer.Add(PositionEntrySizer, 0, wx.EXPAND | wx.ALL, 5)
        
        PlayerY_txt = wx.StaticText(PositionPanel, -1,"Player Y:")
        PositionEntrySizer.Add(PlayerY_txt, (0, 0), wx.DefaultSpan,  wx.ALL, 6)
        self.PlayerY = wx.SpinCtrl(PositionPanel, -1,style=wx.TE_CENTRE, size=(60,-1))
        self.PlayerY.SetRange(0,127)
        self.PlayerY.Bind(wx.EVT_TEXT, self.PosEdit.ChangePlayerY)
        PositionEntrySizer.Add(self.PlayerY,(0, 1), wx.DefaultSpan,  wx.ALL, 4)
        
        EnemyY_txt = wx.StaticText(PositionPanel, -1,"Enemy Y:")
        PositionEntrySizer.Add(EnemyY_txt, (1, 0), wx.DefaultSpan,  wx.ALL, 6)
        self.EnemyY = wx.SpinCtrl(PositionPanel, -1,style=wx.TE_CENTRE, size=(60,-1))
        self.EnemyY.SetRange(0,127)
        self.EnemyY.Bind(wx.EVT_TEXT, self.PosEdit.ChangeEnemyY)
        PositionEntrySizer.Add(self.EnemyY,(1, 1), wx.DefaultSpan,  wx.ALL, 4)
        
        EnemyAlt_txt = wx.StaticText(PositionPanel, -1,"Enemy Altitude:")
        PositionEntrySizer.Add(EnemyAlt_txt, (2, 0), wx.DefaultSpan,  wx.ALL, 6)
        self.EnemyAlt = wx.SpinCtrl(PositionPanel, -1,style=wx.TE_CENTRE, size=(60,-1))
        self.EnemyAlt.SetRange(0,127)
        self.EnemyAlt.Bind(wx.EVT_TEXT, self.PosEdit.ChangeEnemyAlt)
        PositionEntrySizer.Add(self.EnemyAlt,(2, 1), wx.DefaultSpan,  wx.ALL, 4)
        
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
        
        IconRepoint = Button(IconPanel, 65, "Repoint Icon")
        self.Bind(wx.EVT_BUTTON, self.RepointIcon, id=65)
        IconPanelSizer.Add(IconRepoint, 0, wx.EXPAND | wx.ALL, 5)
        
        self.IconPalChoice = ComboBox(IconPanel, -1, choices=[],
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
        PalettePanel.Layout()
        spritePanel.Layout()
        PositionPanel.Layout()
        IconPanel.Layout()
        self.Layout()
    
    def OnChangePointers(self, instance):
        if self.NoLoad:
            return
        Repointer = ChangeSpritePointers(self)
        Repointer.FS.SetValue(hex(self.FrontSpritePointer))
        Repointer.BS.SetValue(hex(self.BackSpritePointer))
        Repointer.NP.SetValue(hex(self.FrontPalettePointer))
        Repointer.SP.SetValue(hex(self.ShinyPalettePointer))
            
        if Repointer.ShowModal() == wx.ID_OK:
            FrontSpriteTable = int(self.config.get(self.rom_id, "FrontSpriteTable"), 0)
            BackSpriteTable = int(self.config.get(self.rom_id, "BackSpriteTable"), 0)
            FrontPaletteTable = int(self.config.get(self.rom_id, "FrontPaletteTable"), 0)
            ShinyPaletteTable = int(self.config.get(self.rom_id, "ShinyPaletteTable"), 0)
            bytes_per_entry = 8
            with open(self.rom_name, "r+b") as rom:
                rom.seek(0)
                backup = rom.read()
                try:
                    rom.seek(FrontSpriteTable+(self.poke_num)*bytes_per_entry)
                    tmp = MakeByteStringPointer(int(Repointer.FS.GetValue(), 0))
                    rom.write(tmp)
                    rom.seek(BackSpriteTable+(self.poke_num)*bytes_per_entry)
                    tmp = MakeByteStringPointer(int(Repointer.BS.GetValue(), 0))
                    rom.write(tmp)
                    rom.seek(FrontPaletteTable+(self.poke_num)*bytes_per_entry)
                    tmp = MakeByteStringPointer(int(Repointer.NP.GetValue(), 0))
                    rom.write(tmp)
                    rom.seek(ShinyPaletteTable+(self.poke_num)*bytes_per_entry)
                    tmp = MakeByteStringPointer(int(Repointer.SP.GetValue(), 0))
                    rom.write(tmp)
                except:
                    ERROR = wx.MessageDialog(None, 
                            "The pointer change has failed. Nothing was changed.", 
                            'Repoint failed.', 
                            wx.OK | wx.ICON_ERROR)
                    ERROR.ShowModal()
                    rom.seek(0)
                    rom.write(backup)
                    return
            self.load_everything(self.poke_num)
        
    def RepointIcon(self, instance):
        if self.NoLoad:
            return
        with open(self.rom_name, "r+b") as rom:
            repointer = SpriteRepointer(rom, 
                                        need=len(self.GBAIcon), 
                                        repoint_what="Icon")
            if repointer.ShowModal() == wx.ID_OK:
                offset = repointer.offset
                if offset == None:
                    ERROR = wx.MessageDialog(None, 
                                "No offset was selected and nothing has been changed.", 
                                'Just letting you know...', 
                                wx.OK | wx.ICON_ERROR)
                    ERROR.ShowModal()
                    return
                iconspritetable = int(self.config.get(self.rom_id, "iconspritetable"), 0)
                rom.seek(iconspritetable+(self.poke_num)*4)
                #Write new pointer
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
                                "You have aborted repoint. Nothing was changed.", 
                                'Just letting you know...', 
                                wx.OK | wx.ICON_ERROR)
                ERROR.ShowModal()
    
    def WarnOverWrite(self, what):
        ERROR = wx.MessageDialog(None,
            "You have chosen to fill the '%s' with free space. However, I have "\
            "detected that there are multiple pointers to this image outside "\
            "of the one that you are using. This means that there may be "\
            "multiple things using this image. Overwriting it could cause "\
            "issues. Should I continue and fill it with free space?"%what, 
            'Multiple Pointers Detected', 
            wx.YES_NO | wx.ICON_ERROR)
        
        if ERROR.ShowModal() == wx.ID_YES: return True
        else: return False
    
    def save(self):
        if self.NoLoad:
            return
        if not self.SeperateFrames.IsChecked():
            self.SaveTogether()
            return
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
        
        bytes_per_entry = 8
        overwrite = self.cb.IsChecked()
        
        with open(self.rom_name, "r+b") as rom:
            rom.seek(0)
            WholeRom = rom.read()
            if self.Changes["front"] != False:
                print "Changing front sprite."
                GBAFrontSprite = ""
                for sprite in self.GBAFrontSpriteFrames:
                    GBAFrontSprite += sprite
                GBAFSLZ = LZCompress(GBAFrontSprite)
                if len(GBAFSLZ) > self.OrgSizes["front"]:
                    repointer = SpriteRepointer(rom, 
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
                                hexOffset = MakeByteStringPointer(offset)
                                rom.write(hexOffset)
                                #Check for shared pointers
                                Pointer = MakeByteStringPointer(self.FrontSpritePointer)
                                PointerList = []
                                index = 0
                                while True:
                                    index = WholeRom.find(Pointer, index)
                                    if index == -1: break
                                    if index%4 == 0:
                                        PointerList.append(index)
                                    index += 4
                                if len(PointerList) > 1:
                                    if self.WarnOverWrite("Front Sprite"):
                                        #Clear old image
                                        if overwrite == True:
                                            rom.seek(self.FrontSpritePointer)
                                            for x in range(self.OrgSizes["front"]):
                                                rom.write("\xFF")
                                else:
                                    #Clear old image
                                    if overwrite == True:
                                        rom.seek(self.FrontSpritePointer)
                                        for x in range(self.OrgSizes["front"]):
                                            rom.write("\xFF")
                                break
                        else: return
                else:
                    rom.seek(self.FrontSpritePointer)
                    rom.write(GBAFSLZ)
                    
            if self.Changes["back"] != False:
                print "Changing back sprite"
                GBABackSprite = ""
                for sprite in self.GBABackSpriteFrames:
                    if sprite != False:
                        GBABackSprite += sprite
                GBABSLZ = LZCompress(GBABackSprite)
                if len(GBABSLZ) > self.OrgSizes["back"]:
                    repointer = SpriteRepointer(rom, 
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
                                hexOffset = MakeByteStringPointer(offset)
                                rom.write(hexOffset)
                                #Check for shared pointers
                                Pointer = MakeByteStringPointer(self.BackSpritePointer)
                                PointerList = []
                                index = 0
                                while True:
                                    index = WholeRom.find(Pointer, index)
                                    if index == -1: break
                                    if index%4 == 0:
                                        PointerList.append(index)
                                    index += 4
                                if len(PointerList) > 1:
                                    if self.WarnOverWrite("Back Sprite"):
                                        #Clear old image
                                        if overwrite == True:
                                            rom.seek(self.BackSpritePointer)
                                            for x in range(self.OrgSizes["back"]):
                                                rom.write("\xFF")
                                else:
                                    #Clear old image
                                    if overwrite == True:
                                        rom.seek(self.BackSpritePointer)
                                        for x in range(self.OrgSizes["back"]):
                                            rom.write("\xFF")
                                        
                                #Write new image
                                rom.seek(offset)
                                if GBABSLZ[-1] == "\xFF":
                                    rom.write(GBABSLZ+"\xFE")
                                    print "GBABSLZ ended in FF"
                                else:
                                    rom.write(GBABSLZ)
                                self.OrgSizes["back"] = len(GBABSLZ)
                                break
                        else: return
                else:
                    rom.seek(self.BackSpritePointer)
                    rom.write(GBABSLZ)
                    
            if self.Changes["normal"] != False:
                print "Changing normal palette"
                normal = Convert25bitPalettetoGBA(self.FrontPalette)
                GBANORMALLZ = LZCompress(normal)
                if len(GBANORMALLZ) > self.OrgSizes["normal"]:
                    repointer = SpriteRepointer(rom, 
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
                                hexOffset = MakeByteStringPointer(offset)
                                rom.write(hexOffset)
                                #Check for shared pointers
                                Pointer = MakeByteStringPointer(self.FrontPalettePointer)
                                PointerList = []
                                index = 0
                                while True:
                                    index = WholeRom.find(Pointer, index)
                                    if index == -1: break
                                    if index%4 == 0:
                                        PointerList.append(index)
                                    index += 4
                                if len(PointerList) > 1:
                                    if self.WarnOverWrite("Normal Palette"):
                                        #Clear old image
                                        if overwrite == True:
                                            rom.seek(self.FrontPalettePointer)
                                            for x in range(self.OrgSizes["normal"]):
                                                rom.write("\xFF")
                                else:
                                    #Clear old image
                                    if overwrite == True:
                                        rom.seek(self.FrontPalettePointer)
                                        for x in range(self.OrgSizes["normal"]):
                                            rom.write("\xFF")
                                #Write new image
                                rom.seek(offset)
                                if GBANORMALLZ[-1] == "\xFF":
                                    rom.write(GBANORMALLZ+"\xFE")
                                    print "GBANORMALLZ ended in FF"
                                else:
                                    rom.write(GBANORMALLZ)
                                self.OrgSizes["normal"] = len(GBANORMALLZ)
                                break
                        else: return
                else:
                    rom.seek(self.FrontPalettePointer)
                    rom.write(GBANORMALLZ)
                    
            if self.Changes["shiny"] != False:
                print "Writing shiny palette"
                shiny = Convert25bitPalettetoGBA(self.ShinyPalette)
                GBASHINYLZ = LZCompress(shiny)
                if len(GBASHINYLZ) > self.OrgSizes["shiny"]:
                    repointer = SpriteRepointer(rom, 
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
                                hexOffset = MakeByteStringPointer(offset)
                                rom.write(hexOffset)
                                #Check for shared pointers
                                Pointer = MakeByteStringPointer(self.ShinyPalettePointer)
                                PointerList = []
                                index = 0
                                while True:
                                    index = WholeRom.find(Pointer, index)
                                    if index == -1: break
                                    if index%4 == 0:
                                        PointerList.append(index)
                                    index += 4
                                if len(PointerList) > 1:
                                    if self.WarnOverWrite("Shiny Palette"):
                                        #Clear old image
                                        if overwrite == True:
                                            rom.seek(self.ShinyPalettePointer)
                                            for x in range(self.OrgSizes["shiny"]):
                                                rom.write("\xFF")
                                else:
                                    #Clear old image
                                    if overwrite == True:
                                        rom.seek(self.ShinyPalettePointer)
                                        for x in range(self.OrgSizes["shiny"]):
                                            rom.write("\xFF")
                                #Write new image
                                rom.seek(offset)
                                if GBASHINYLZ[-1] == "\xFF":
                                    rom.write(GBASHINYLZ+"\xFE")
                                    print "GBASHINYLZ ended in FF"
                                else:
                                    rom.write(GBASHINYLZ)
                                self.OrgSizes["shiny"] = len(GBASHINYLZ)
                                break
                        else: return
                else:
                    rom.seek(self.ShinyPalettePointer)
                    rom.write(GBASHINYLZ)
            #Write positions
            rom.seek(playerytable+(self.poke_num)*4+1)
            PlayerY = hex(self.PlayerY.GetValue()).rstrip("L").lstrip("0x").zfill(2)
            rom.write(unhexlify(PlayerY))
            
            rom.seek(enemyaltitudetable+(self.poke_num))
            EnemyAlt = hex(self.EnemyAlt.GetValue()).rstrip("L").lstrip("0x").zfill(2)
            rom.write(unhexlify(EnemyAlt))
            
            rom.seek(enemyytable+(self.poke_num)*4+1)
            EnemyY = hex(self.EnemyY.GetValue()).rstrip("L").lstrip("0x").zfill(2)
            rom.write(unhexlify(EnemyY))
            
            #Write all things Icon
            rom.seek(self.IconPointer)
            rom.write(self.GBAIcon)
            
            rom.seek(iconpalettetable+(self.poke_num))
            rom.write(unhexlify(hex(self.IconPalNum).rstrip("L").lstrip("0x").zfill(2)))
            
            pals = ""
            for pal in self.IconPals:
                tmp = Convert25bitPalettetoGBA(pal)
                pals += tmp
            rom.seek(iconpalettes)
            rom.write(pals)
            for opt in self.Changes:
                self.Changes[opt] = False
    
    def SaveTogether(self):
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
        
        bytes_per_entry = 8
        overwrite = self.cb.IsChecked()
        
        RepointList = []
        with open(self.rom_name, "r+b") as rom:
            if self.Changes["front"] != False:
                GBAFrontSprite = ""
                for sprite in self.GBAFrontSpriteFrames:
                    GBAFrontSprite += sprite
                GBAFSLZ = LZCompress(GBAFrontSprite)
                if len(GBAFSLZ) > self.OrgSizes["front"]:
                    RepointList.append((GBAFSLZ,FrontSpriteTable,self.FrontSpritePointer,"front"))
                else:
                    rom.seek(self.FrontSpritePointer)
                    rom.write(GBAFSLZ)
            if self.Changes["back"] != False:
                GBABackSprite = ""
                for sprite in self.GBABackSpriteFrames:
                    if sprite != False:
                        GBABackSprite += sprite
                GBABSLZ = LZCompress(GBABackSprite)
                if len(GBABSLZ) > self.OrgSizes["back"]:
                    RepointList.append((GBABSLZ,BackSpriteTable,self.BackSpritePointer,"back"))
                else:
                    rom.seek(self.BackSpritePointer)
                    rom.write(GBABSLZ)
            if self.Changes["normal"] != False:
                normal = Convert25bitPalettetoGBA(self.FrontPalette)
                GBANORMALLZ = LZCompress(normal)
                if len(GBANORMALLZ) > self.OrgSizes["normal"]:
                    RepointList.append((GBANORMALLZ,FrontPaletteTable,self.FrontPalettePointer,"normal"))
                else:
                    rom.seek(self.FrontPalettePointer)
                    rom.write(GBANORMALLZ)
            if self.Changes["shiny"] != False:
                shiny = Convert25bitPalettetoGBA(self.ShinyPalette)
                GBASHINYLZ = LZCompress(shiny)
                if len(GBASHINYLZ) > self.OrgSizes["shiny"]:
                    RepointList.append((GBASHINYLZ,ShinyPaletteTable,self.ShinyPalettePointer,"shiny"))
                else:
                    rom.seek(self.ShinyPalettePointer)
                    rom.write(GBASHINYLZ)
            if RepointList != []:
                rom.seek(0)
                WholeRom = rom.read()
                Length = ""
                for x in RepointList:
                    Length += x[0]
                repointer = SpriteRepointer(rom,need=len(Length)+16,repoint_what="Sprites")
                while True:
                    if repointer.ShowModal() == wx.ID_OK:
                        if repointer.offset == None: continue
                        else:
                            start = repointer.offset
                            ShouldIOverwrite = True
                            for sprite in RepointList:
                                #Check for shared pointers
                                Pointer = MakeByteStringPointer(sprite[2])
                                PointerList = []
                                index = 0
                                while True:
                                    index = WholeRom.find(Pointer, index)
                                    if index == -1: break
                                    if index%4 == 0:
                                        PointerList.append(index)
                                    index += 4
                                if len(PointerList) > 1:
                                    ShouldIOverwrite = self.WarnOverWrite("sprite and palette")
                                    break
                            for sprite in RepointList:
                                rom.seek(sprite[1]+(self.poke_num)*bytes_per_entry)
                                #Write new pointer
                                hexOffset = MakeByteStringPointer(start)
                                rom.write(hexOffset)
                                if ShouldIOverwrite:
                                    #Clear old image
                                    if overwrite == True:
                                        rom.seek(sprite[2])
                                        for x in range(self.OrgSizes[sprite[3]]):
                                            rom.write("\xFF")
                                #Write new image
                                rom.seek(start)
                                if sprite[0][-1] == "\xFF":
                                    rom.write(sprite[0]+"\xFE")
                                    print "Sprite/Palette ended in FF"
                                else:
                                    rom.write(sprite[0])
                                start = rom.tell()
                                while start%4:
                                    start += 1
                                self.OrgSizes[sprite[3]] = len(sprite[0])
                            break
                    else: return
            #Write positions
            rom.seek(playerytable+(self.poke_num)*4+1)
            PlayerY = hex(self.PlayerY.GetValue()).rstrip("L").lstrip("0x").zfill(2)
            rom.write(unhexlify(PlayerY))
            
            rom.seek(enemyaltitudetable+(self.poke_num))
            EnemyAlt = hex(self.EnemyAlt.GetValue()).rstrip("L").lstrip("0x").zfill(2)
            rom.write(unhexlify(EnemyAlt))
            
            rom.seek(enemyytable+(self.poke_num)*4+1)
            EnemyY = hex(self.EnemyY.GetValue()).rstrip("L").lstrip("0x").zfill(2)
            rom.write(unhexlify(EnemyY))
            #Write all things Icon
            rom.seek(self.IconPointer)
            rom.write(self.GBAIcon)
            
            rom.seek(iconpalettetable+(self.poke_num))
            rom.write(unhexlify(hex(self.IconPalNum).rstrip("L").lstrip("0x").zfill(2)))
            
            pals = ""
            for pal in self.IconPals:
                tmp = Convert25bitPalettetoGBA(pal)
                pals += tmp
            rom.seek(iconpalettes)
            rom.write(pals)
            for opt in self.Changes:
                self.Changes[opt] = False

                
    def SwapIconPal(self, instance):
        if self.NoLoad:
            return
        self.IconPalNum = instance.GetSelection()
        self.ReloadShownSprites()
        
    def editIconColor(self, instance):
        if self.NoLoad:
            return
        instance = instance.GetEventObject()
        color_number = instance.Id-70
        dlg = wx.ColourDialog(self)
        dlg.GetColourData().SetChooseFull(True)
        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.GetColourData()
        else: return
        wx.CallAfter(dlg.Destroy)
        self.IconPals[self.IconPalNum][color_number] = data.GetColour()
        self.ReloadShownSprites()
    
    def edit_color(self, instance):
        if self.NoLoad:
            return
        instance = instance.GetEventObject()
        
        frame = self.Frames.GetValue()
        if len(self.FrontPalette) < (frame+1)*16:
            start = 0
        else:
            start = frame*16
        
        color_number = instance.Id
        dlg = wx.ColourDialog(self)
        dlg.GetColourData().SetChooseFull(True)
        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.GetColourData()
        else: return
        wx.CallAfter(dlg.Destroy)
        if color_number < 16:
            self.FrontPalette[start+color_number] = data.GetColour()
            self.Changes["normal"]=True
        else:
            self.ShinyPalette[start+(color_number-16)] = data.GetColour()
            self.Changes["shiny"]=True
        self.ReloadShownSprites()
    
    def LoadIcon(self, instance):
        if self.NoLoad:
            return
        wildcard = "PNG (*.png)|*.png|GIF (*.gif)|*.gif|All files (*.*)|*.*"
        open_dialog = wx.FileDialog(self, message="Open an icon...", 
                                    defaultDir=self.lastPath, style=wx.OPEN,
                                    wildcard=wildcard)
        if open_dialog.ShowModal() == wx.ID_OK:
            filename = open_dialog.GetPath()
            self.lastPath = os.path.dirname(filename)
            raw = Image.open(filename)
            if raw.size != (32,64):
                ERROR = wx.MessageDialog(self,
                        "Image is "+str(raw.size[0])+"x"+str(raw.size[1])+". It must be 32x64.", 
                        'Image Size error', 
                        wx.OK | wx.ICON_ERROR)
                ERROR.ShowModal()
                return
            if raw.mode != "P":
                raw = raw.convert("RGB")
                converted = raw.convert("P", palette=Image.ADAPTIVE, colors=16)
            else:
                if len(raw.getcolors()) > 16:
                    tmp = raw.convert("RGB")
                    converted = raw.convert("P", palette=Image.ADAPTIVE, colors=16)
                else: converted = raw
            converted = converted.convert("RGB")
            image = PilImageToWxImage(converted)
            OrgPalette = GetImageColors(image)
            
            BestPaletteIndex = BestPalette(self.IconPals,OrgPalette)
            IconPalette = self.IconPals[BestPaletteIndex]
            
            TC = IconPalette[0]
            TransColor = (TC[0],TC[1],TC[2])
            
            PILPal = []
            for color in IconPalette:
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
            
            self.IconPalNum = BestPaletteIndex
            self.IconPalChoice.SetSelection(BestPaletteIndex)
            self.GBAIcon, palette = ConvertNormalImageToGBA(image, palette=IconPalette, size=(32,64))
            self.TMPIcon = ConvertGBAImageToNormal(self.GBAIcon,IconPalette,size=(32,64))
            self.Icons.SetBitmapLabel(self.TMPIcon)
            self.ReloadShownSprites()
    
    def ReloadShownSprites(self, *args):
        if self.NoLoad:
            return
        frame = self.Frames.GetValue()
        if len(self.FrontPalette) < (frame+1)*16:
            start = 0
            stop = 16
        else:
            start = frame*16
            stop = (frame+1)*16
        if self.GBABackSpriteFrames[frame] != False:
            self.TMPFrontSprite = ConvertGBAImageToNormal(self.GBAFrontSpriteFrames[frame],self.FrontPalette[start:stop])
            self.TMPBackSprite = ConvertGBAImageToNormal(self.GBABackSpriteFrames[frame],self.FrontPalette[start:stop])
            self.TMPSFrontSprite = ConvertGBAImageToNormal(self.GBAFrontSpriteFrames[frame],self.ShinyPalette[start:stop])
            self.TMPSBackSprite = ConvertGBAImageToNormal(self.GBABackSpriteFrames[frame],self.ShinyPalette[start:stop])
            self.FrontSprite.SetBitmapLabel(self.TMPFrontSprite)
            self.BackSprite.SetBitmapLabel(self.TMPBackSprite)
            self.SFrontSprite.SetBitmapLabel(self.TMPSFrontSprite)
            self.SBackSprite.SetBitmapLabel(self.TMPSBackSprite)
        else:
            self.TMPFrontSprite = ConvertGBAImageToNormal(self.GBAFrontSpriteFrames[frame],self.FrontPalette[start:stop])
            self.TMPSFrontSprite = ConvertGBAImageToNormal(self.GBAFrontSpriteFrames[frame],self.ShinyPalette[start:stop])
        
            self.FrontSprite.SetBitmapLabel(self.TMPFrontSprite)
            self.BackSprite.SetBitmapLabel(wx.EmptyBitmapRGBA(64,64,alpha=255))
            self.SFrontSprite.SetBitmapLabel(self.TMPSFrontSprite)
            self.SBackSprite.SetBitmapLabel(wx.EmptyBitmapRGBA(64,64,alpha=255))
            
        self.TMPIcon = ConvertGBAImageToNormal(self.GBAIcon,self.IconPals[self.IconPalNum],size=(32,64))
        self.Icons.SetBitmapLabel(self.TMPIcon)
        
        for num, color in enumerate(self.FrontPalette[start:stop]):
            self.ColorButtons[num].SetBackgroundColour(color)
        for num, color in enumerate(self.ShinyPalette[start:stop]):
            self.ColorButtons[num+16].SetBackgroundColour(color)
        for num, color in enumerate(self.IconPals[self.IconPalNum]):
            self.IconColorButtons[num].SetBackgroundColour(color)
            
        tmpimage = wx.ImageFromBitmap(self.TMPIcon)
            
        self.IconTop = tmpimage.GetSubImage((0,0,32,32)).Scale(64, 64)
        self.IconBottom = tmpimage.GetSubImage((0,32,32,32)).Scale(64, 64)
        
        self.IconTop = wx.BitmapFromImage(self.IconTop)
        self.IconBottom = wx.BitmapFromImage(self.IconBottom)
        self.PosEdit.UpdateFSandDS(self)
        
    def LoadSingleSprite(self, instance):
        if self.NoLoad:
            return
        frame = self.Frames.GetValue()
        if len(self.FrontPalette) < (frame+1)*16:
            start = 0
            stop = 16
        else:
            start = frame*16
            stop = (frame+1)*16
        instance = instance.GetEventObject()
        sprite_number = instance.Id
        if sprite_number == 57 or sprite_number == 59:
            if self.GBABackSpriteFrames[frame] == False:
                return
        wildcard = "PNG (*.png)|*.png|GIF (*.gif)|*.gif|All files (*.*)|*.*"
        open_dialog = wx.FileDialog(self, message="Open a sprite...", 
                                    defaultDir=self.lastPath, style=wx.OPEN,
                                    wildcard=wildcard)
        if open_dialog.ShowModal() == wx.ID_OK:
            filename = open_dialog.GetPath()
            self.lastPath = os.path.dirname(filename)
            raw = Image.open(filename)
            
            if raw.size != (64,64):
                ERROR = wx.MessageDialog(self,
                        "Image is "+str(raw.size[0])+"x"+str(raw.size[1])+". It must be 64x64.", 
                        'Image Size error', 
                        wx.OK | wx.ICON_ERROR)
                ERROR.ShowModal()
                return
            if raw.mode != "P":
                raw = raw.convert("RGB")
                converted = raw.convert("P", palette=Image.ADAPTIVE, colors=16)
            else:
                if len(raw.getcolors()) > 16:
                    tmp = raw.convert("RGB")
                    converted = raw.convert("P", palette=Image.ADAPTIVE, colors=16)
                else: converted = raw
            image = PilImageToWxImage(converted)
            gbaversion, palette = ConvertNormalImageToGBA(image)
            
            if sprite_number == 56:
                self.GBAFrontSpriteFrames[frame] = gbaversion
                self.FrontPalette[start:stop] = palette
                self.Changes["front"]=True
                self.Changes["normal"]=True
            elif sprite_number == 57:
                self.GBABackSpriteFrames[frame] = gbaversion
                self.FrontPalette[start:stop] = palette
                self.Changes["back"]=True
                self.Changes["normal"]=True
            elif sprite_number == 58:
                self.GBAFrontSpriteFrames[frame] = gbaversion
                self.ShinyPalette[start:stop] = palette
                self.Changes["front"]=True
                self.Changes["shiny"]=True
            elif sprite_number == 59:
                self.GBABackSpriteFrames[frame] = gbaversion
                self.ShinyPalette[start:stop] = palette
                self.Changes["back"]=True
                self.Changes["shiny"]=True
            self.ReloadShownSprites()
            
    def LoadSheetSprite(self, instance):
        if self.NoLoad:
            return
        wildcard = "PNG (*.png)|*.png|GIF (*.gif)|*.gif|All files (*.*)|*.*"
        open_dialog = wx.FileDialog(self, message="Open a sprite sheet...", 
                                                        defaultDir=self.lastPath, style=wx.OPEN,wildcard=wildcard)
        if open_dialog.ShowModal() == wx.ID_OK:
            frame = self.Frames.GetValue()
            if len(self.FrontPalette) < (frame+1)*16:
                start = 0
                stop = 16
            else:
                start = frame*16
                stop = (frame+1)*16
            filename = open_dialog.GetPath()
            self.lastPath = os.path.dirname(filename)
            raw = Image.open(filename)
            if raw.size != (256,64):
                ERROR = wx.MessageDialog(self,
                    "Image is "+str(raw.size[0])+"x"+str(raw.size[1])+". It must be 256x64.", 
                    'Image Size error', 
                    wx.OK | wx.ICON_ERROR)
                ERROR.ShowModal()
                return
            if self.GBABackSpriteFrames[frame] != False:
                front = raw.copy().crop((0, 0, 64, 64))
                shiny = raw.copy().crop((64, 0, 128, 64))
                back = raw.copy().crop((128, 0, 192, 64))
                frontback = Image.new("RGB", (128,64))
                frontback.paste(front, (0,0))
                frontback.paste(back, (64,0))
                if frontback.mode != "P":
                    frontback = frontback.convert("RGB")
                    frontback = frontback.convert("P", palette=Image.ADAPTIVE, colors=16)
                else:
                    if len(frontback.getcolors()) > 16:
                        tmp = frontback.convert("RGB")
                        frontback = tmp.convert("P", palette=Image.ADAPTIVE, colors=16)
                if shiny.mode != "P":
                    shiny = shiny.convert("RGB")
                    shiny = shiny.convert("P", palette=Image.ADAPTIVE, colors=16)
                else:
                    if len(shiny.getcolors()) > 16:
                        tmp = shiny.convert("RGB")
                        shiny = tmp.convert("P", palette=Image.ADAPTIVE, colors=16)
                front = frontback.copy().crop((0, 0, 64, 64))
                back = frontback.copy().crop((64, 0, 128, 64))
                wxfront = PilImageToWxImage(front)
                self.GBAFrontSpriteFrames[frame], self.FrontPalette[start:stop] = ConvertNormalImageToGBA(wxfront)
                wxback = PilImageToWxImage(back)
                self.GBABackSpriteFrames[frame], tmp = ConvertNormalImageToGBAUnderPal(wxback, self.FrontPalette[start:stop])
                
                self.ShinyPalette[start:stop] = GetShinyPalette(front.convert("RGB"), shiny.convert("RGB"), self.FrontPalette[start:stop])
                self.ReloadShownSprites()
                self.Changes["front"]=True
                self.Changes["back"]=True
                self.Changes["normal"]=True
                self.Changes["shiny"]=True
            
            else:
                front = raw.copy().crop((0, 0, 64, 64))
                if front.mode != "P":
                    front = front.convert("P", palette=Image.ADAPTIVE, colors=16)
                else:
                    if len(front.getcolors()) > 16:
                        tmp = front.convert("RGB")
                        front = tmp.convert("P", palette=Image.ADAPTIVE, colors=16)
                wxfront = PilImageToWxImage(front)
                self.GBAFrontSpriteFrames[frame],  tmp = ConvertNormalImageToGBAUnderPal(wxfront,self.FrontPalette[start:stop])
                self.ReloadShownSprites()
                self.Changes["front"]=True
                
    def load_everything(self, poke_num):
        self.cb.SetValue(False)
        self.NoLoad = False
        self.Frames.SetValue(0)
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
        
        bytes_per_entry = 8
        
        with open(self.rom_name, "r+b") as rom:
            rom.seek(FrontSpriteTable+(poke_num)*bytes_per_entry)
            FSPoint = rom.read(4)
            self.FrontSpritePointer = read_pointer(FSPoint)
            rom.seek(BackSpriteTable+(poke_num)*bytes_per_entry)
            BSPoint = rom.read(4)
            self.BackSpritePointer = read_pointer(BSPoint)
            rom.seek(FrontPaletteTable+(poke_num)*bytes_per_entry)
            NPPoint = rom.read(4)
            self.FrontPalettePointer = read_pointer(NPPoint)
            rom.seek(ShinyPaletteTable+(poke_num)*bytes_per_entry)
            SPPoint = rom.read(4)
            self.ShinyPalettePointer = read_pointer(SPPoint)
            
            self.GBAFrontSprite, self.OrgSizes["front"] = LZUncompress(rom, self.FrontSpritePointer)
            if self.GBAFrontSprite == False or self.OrgSizes["front"] == False:
                self.imageLoadingError(hexlify(FSPoint))
                return
            self.GBABackSprite, self.OrgSizes["back"] = LZUncompress(rom, self.BackSpritePointer)
            if self.GBABackSprite == False or self.OrgSizes["back"] == False:
                self.imageLoadingError(hexlify(BSPoint))
                return
            FrontPalette, self.OrgSizes["normal"] = LZUncompress(rom, self.FrontPalettePointer)
            if FrontPalette == False or self.OrgSizes["normal"] == False:
                self.imageLoadingError(hexlify(NPPoint))
                return
            ShinyPalette, self.OrgSizes["shiny"] = LZUncompress(rom, self.ShinyPalettePointer)
            if ShinyPalette == False or self.OrgSizes["shiny"] == False:
                self.imageLoadingError(hexlify(SPPoint))
                return
            
                
            self.GBAFrontSpriteFrames = []
            self.GBABackSpriteFrames = []
            
            NumberOfFrames = len(self.GBAFrontSprite)/2048
            self.Frames.SetRange(0,NumberOfFrames-1)
            for x in range(NumberOfFrames):
                self.GBAFrontSpriteFrames.append(self.GBAFrontSprite[x*2048:(x+1)*2048])
                if len(self.GBABackSprite)/2048 < x+1:
                    self.GBABackSpriteFrames.append(False)
                else:
                    self.GBABackSpriteFrames.append(self.GBABackSprite[x*2048:(x+1)*2048])
            
            self.FrontPalette = ConvertGBAPalTo25Bit(FrontPalette)
            self.ShinyPalette = ConvertGBAPalTo25Bit(ShinyPalette)
            
            self.TMPFrontSprite = ConvertGBAImageToNormal(self.GBAFrontSpriteFrames[0],self.FrontPalette)
            self.TMPBackSprite = ConvertGBAImageToNormal(self.GBABackSpriteFrames[0],self.FrontPalette)
            self.TMPSFrontSprite = ConvertGBAImageToNormal(self.GBAFrontSpriteFrames[0],self.ShinyPalette)
            self.TMPSBackSprite = ConvertGBAImageToNormal(self.GBABackSpriteFrames[0],self.ShinyPalette)
            self.Refresh()
            
            TMPFS = wx.BitmapFromImage(self.TMPFrontSprite.ConvertToImage())
            TMPSBS = wx.BitmapFromImage(self.TMPSBackSprite.ConvertToImage())
            self.PosEdit.LoadFSandBS(TMPFS,TMPSBS)
            del TMPFS
            del TMPSBS
            
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
            
            self.PosEdit.RECTS[0] = 48+self.PlayerY.GetValue()
            self.PosEdit.RECTS[2] = self.EnemyAlt.GetValue()
            self.PosEdit.EnemyY = self.EnemyY.GetValue()
            self.PosEdit.RECTS[1] = 8+self.PosEdit.EnemyY-self.PosEdit.RECTS[2]
            
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
            if num > 15: break
            self.ColorButtons[num].SetBackgroundColour(color)
        for num, color in enumerate(self.ShinyPalette):
            if num > 15: break
            self.ColorButtons[num+16].SetBackgroundColour(color)
        for num, color in enumerate(self.IconPals[self.IconPalNum]):
            if num > 15: break
            self.IconColorButtons[num].SetBackgroundColour(color)
        nums = []
        for n in range(numiconpalettes):
            nums.append(str(n))
        self.IconPalChoice.Clear()
        self.IconPalChoice.AppendItems(nums) 
        self.IconPalChoice.SetSelection(self.IconPalNum)
    
    def imageLoadingError(self, pointer):
        ERROR = wx.MessageDialog(None, 
                "Images failed to decompress. Aborting sprite load.\nThe image that was attempted to be loaded had pointer: {0}".format(pointer), 
                'Error loading sprite data...', 
                wx.OK | wx.ICON_ERROR)
        ERROR.ShowModal()
        Recovery()
        self.NoLoad = True
    
    def OnIconTimer1(self, event):
        self.Icontimer.Stop()
        self.SetIconTimer(2)
        self.AniIcon.SetBitmapLabel(self.IconTop)
        
    def OnIconTimer2(self, event):
        self.Icontimer.Stop()
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
        
        if self.repoint[-1:] == "s":
            RepointWhat = self.repoint+" need to be repointed.\n\n"
        else:
            RepointWhat = self.repoint+" needs to be repointed.\n\n"
        txt = wx.StaticText(self, -1, RepointWhat ,style=wx.TE_CENTRE)
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
        self.rom.seek(0)
        read = self.rom.read()
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


class ChangeSpritePointers(wx.Dialog):
    def __init__(self, obj, *args, **kw):
        wx.Dialog.__init__(self, parent=obj, id=wx.ID_ANY)
        self.SetWindowStyle( self.GetWindowStyle() | wx.STAY_ON_TOP | wx.RESIZE_BORDER )
        
        self.InitUI()
        self.SetTitle("Change Sprite Pointers")
        
    def InitUI(self):
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        txt = wx.StaticText(self, -1, textwrap.fill("Here you can change the pointers for the sprites and palettes. When you click 'OK', the changes will be applied and the sprite tab will be reloaded. You can use hex (prefix with '0x') or decimal (no prefix) or binary (if it pleases you:P, use a '0b' prefix).",90),style=wx.TE_CENTRE)
        vbox.Add(txt, 0, wx.EXPAND | wx.ALL, 5)
        
        GRID = wx.GridBagSizer(4,2)
        vbox.Add(GRID, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 0)
        
        FS_txt = wx.StaticText(self, -1, "Front Sprite:",style=wx.TE_CENTRE)
        GRID.Add(FS_txt, (0,0), wx.DefaultSpan,  wx.ALL, 5)
        self.FS = wx.TextCtrl(self, -1,style=wx.TE_CENTRE, size=(100,-1))
        GRID.Add(self.FS, (0,1), wx.DefaultSpan,  wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        
        BS_txt = wx.StaticText(self, -1, "Back Sprite:",style=wx.TE_CENTRE)
        GRID.Add(BS_txt, (1,0), wx.DefaultSpan,  wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        self.BS = wx.TextCtrl(self, -1,style=wx.TE_CENTRE, size=(100,-1))
        GRID.Add(self.BS, (1,1), wx.DefaultSpan,  wx.ALL, 5)
        
        NP_txt = wx.StaticText(self, -1, "Normal Palette:",style=wx.TE_CENTRE)
        GRID.Add(NP_txt, (2,0), wx.DefaultSpan,  wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        self.NP = wx.TextCtrl(self, -1,style=wx.TE_CENTRE, size=(100,-1))
        GRID.Add(self.NP, (2,1), wx.DefaultSpan,  wx.ALL, 5)
        
        SP_txt = wx.StaticText(self, -1, "Shiny Palette:",style=wx.TE_CENTRE)
        GRID.Add(SP_txt, (3,0), wx.DefaultSpan,  wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        self.SP = wx.TextCtrl(self, -1,style=wx.TE_CENTRE, size=(100,-1))
        GRID.Add(self.SP, (3,1), wx.DefaultSpan,  wx.ALL, 5)
        
        OK = self.CreateButtonSizer(wx.OK)
        vbox.Add(OK, 0, wx.EXPAND | wx.ALL, 5)
        
        self.SetSizerAndFit(vbox)
        self.Fit()
        self.SetMinSize(self.GetEffectiveMinSize())
        
        
