import wx
from binascii import hexlify, unhexlify

from GLOBALS import Globals
from lib.OverLoad.Button import Button, ComboBox
from lib.Tools.rom_insertion_operations import make_pointer
from lib.Tools.rom_insertion_operations import get_hex_from_string

#############################################################
##---------------------Extra Dialogues---------------------##
#############################################################

class MOVE_REPOINTER(wx.Dialog):
    def __init__(self, parent, frame, *args, **kw):
        wx.Dialog.__init__(self, parent=parent, id=wx.ID_ANY)
        self.SetWindowStyle( self.GetWindowStyle() | wx.RESIZE_BORDER )

        self.num = None

        self.InitUI()
        self.SetTitle("Repoint")
        self.frame = frame

    def InitUI(self):
        pnl = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        txt = wx.StaticText(pnl, -1, "How many moves would you like the\nnew move set to be?")
        vbox.Add(txt, 0, wx.EXPAND | wx.ALL, 5)

        self.New_Move_Num = wx.TextCtrl(pnl, -1,style=wx.TE_CENTRE, size=(50,-1))
        vbox.Add(self.New_Move_Num, 0, wx.EXPAND | wx.ALL, 5)

        SEARCH = Button(pnl, 1, "Search")
        self.Bind(wx.EVT_BUTTON, self.OnSearch, id=1)
        vbox.Add(SEARCH, 0, wx.EXPAND | wx.ALL, 5)

        txt2 = wx.StaticText(pnl, -1, "Please choose an offset to repoint to or specify\na manual offset. If a manual offset is specified,\nthe list choice will be ignored.\nNOTE: Manual offsets will NOT be checked for\nfree space availability.\nFor both, please provide the number of moves you\nexpect. It will not continue without it.",style=wx.TE_CENTRE)
        vbox.Add(txt2, 0, wx.EXPAND | wx.ALL, 5)

        self.OFFSETS = wx.ListBox(pnl, -1)
        vbox.Add(self.OFFSETS, 0, wx.EXPAND | wx.ALL, 5)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        manual_txt = wx.StaticText(pnl, -1, "Manual Offset: 0x",style=wx.TE_CENTRE)
        hbox.Add(manual_txt, 0, wx.EXPAND | wx.LEFT|wx.TOP|wx.BOTTOM, 5)
        self.MANUAL = wx.TextCtrl(pnl, -1,style=wx.TE_CENTRE, size=(100,-1))
        hbox.Add(self.MANUAL, 0, wx.EXPAND | wx.RIGHT|wx.TOP|wx.BOTTOM, 5)
        vbox.Add(hbox, 0, wx.EXPAND | wx.ALL, 0)

        self.cb = wx.CheckBox(pnl, -1, 'Fill old table with 0xFF?', (10, 10))
        self.cb.SetValue(True)
        vbox.Add(self.cb, 0, wx.ALL|wx.ALIGN_CENTER, 5)

        SUBMIT = Button(pnl, 2, "Submit")
        self.Bind(wx.EVT_BUTTON, self.OnSubmit, id=2)
        vbox.Add(SUBMIT, 0, wx.EXPAND | wx.ALL, 5)

        pnl.SetSizerAndFit(vbox)
        self.Fit()
        self.SetMinSize(self.GetEffectiveMinSize())

    def OnSubmit(self, *args):
        sel = self.OFFSETS.GetSelection()
        offset = self.MANUAL.GetValue()
        new_offset = None
        if self.num == None:
            try: self.num = int(self.New_Move_Num.GetValue(), 0)
            except: return
        if offset != "":
            if len(offset) > 6:
                check = offset[-7:-6]
                if check == "1" or check == "9":
                    check = "1"
                else:
                    check = ""
                offset = check+offset[-6:].zfill(6)
            new_offset = offset.zfill(6)
            self.frame.tabbed_area.PokeDataTab.tabbed_area.moves.NEW_LEARNED_OFFSET = new_offset
            self.frame.tabbed_area.PokeDataTab.tabbed_area.moves.LEARNED_OFFSET.SetLabel("0x"+new_offset)
            self.frame.tabbed_area.PokeDataTab.tabbed_area.moves.NEW_NUMBER_OF_MOVES = self.num
            self.frame.tabbed_area.PokeDataTab.tabbed_area.moves.UPDATE_FRACTION()
        elif sel != -1:
            new_offset = self.OFFSETS.GetString(sel)[2:]
            self.frame.tabbed_area.PokeDataTab.tabbed_area.moves.NEW_LEARNED_OFFSET = new_offset
            self.frame.tabbed_area.PokeDataTab.tabbed_area.moves.LEARNED_OFFSET.SetLabel("0x"+new_offset)
            self.frame.tabbed_area.PokeDataTab.tabbed_area.moves.NEW_NUMBER_OF_MOVES = self.num
            self.frame.tabbed_area.PokeDataTab.tabbed_area.moves.UPDATE_FRACTION()
        if new_offset != None:
            learned_moves_pointer = int(Globals.INI.get(Globals.OpenRomID, "LearnedMoves"), 0)
            int_offset = int(new_offset,16)+int("8000000",16)
            offset = hex(int_offset)[2:].zfill(8)
            pointer = make_pointer(offset)
            pointer = get_hex_from_string(pointer)
            global poke_num
            offset_of_pointer = learned_moves_pointer+(poke_num)*4
            with open(Globals.OpenRomName, "r+b") as rom:
                rom.seek(offset_of_pointer)
                rom.write(pointer)

                rom.seek(int(new_offset,16))
                Jambo51HackCheck = Globals.INI.get(Globals.OpenRomID, "Jambo51LearnedMoveHack")
                if Jambo51HackCheck == "False":
                    learnedmoveslength = int(Globals.INI.get(Globals.OpenRomID, "learnedmoveslength"), 0)
                    amount_of_bytes = self.num*learnedmoveslength
                    for n in range(int(amount_of_bytes/2)):
                        rom.write("\x00\xCA")
                    rom.write("\xff\xff\xfe\xfe")
                else:
                    amount_of_bytes = self.num*3
                    for n in range(int(amount_of_bytes/2)):
                        rom.write("\x00\xCA")
                    rom.write("\xff\xff\xff\xfe")

            self.OnClose()

    def OnSearch(self, *args):
        self.OFFSETS.Clear()
        try:
            self.num = int(self.New_Move_Num.GetValue(), 0)
        except:
            return
        search = "\xff\xff"*self.num
        with open(Globals.OpenRomName, "r+b") as rom:
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

    def OnClose(self, *args):
        wx.CallAfter(self.Close)

class EGG_MOVE_REPOINTER(wx.Dialog):
    def __init__(self, parent, need, *args, **kw):
        wx.Dialog.__init__(self, parent=parent, id=wx.ID_ANY)
        self.SetWindowStyle( self.GetWindowStyle() | wx.STAY_ON_TOP | wx.RESIZE_BORDER )
        self.NewEggOffset = None
        self.num = need
        self.InitUI()
        self.OnSearch()
        self.SetTitle("Repoint Egg Moves")

    def InitUI(self):
        pnl = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        txt2 = wx.StaticText(pnl, -1, "Egg Moves need to be repointed.\n\n\nPlease choose an offset to repoint to or specify\na manual offset. If a manual offset is specified,\nthe list choice will be ignored.\nNOTE: Manual offsets will NOT be checked for\nfree space availability.",style=wx.TE_CENTRE)
        vbox.Add(txt2, 0, wx.EXPAND | wx.ALL, 5)

        self.OFFSETS = wx.ListBox(pnl, -1)
        vbox.Add(self.OFFSETS, 0, wx.EXPAND | wx.ALL, 5)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        manual_txt = wx.StaticText(pnl, -1, "Manual Offset: 0x",style=wx.TE_CENTRE)
        hbox.Add(manual_txt, 0, wx.EXPAND | wx.LEFT|wx.TOP|wx.BOTTOM, 5)
        self.MANUAL = wx.TextCtrl(pnl, -1,style=wx.TE_CENTRE, size=(100,-1))
        hbox.Add(self.MANUAL, 0, wx.EXPAND | wx.RIGHT|wx.TOP|wx.BOTTOM, 5)
        vbox.Add(hbox, 0, wx.EXPAND | wx.ALL, 0)

        SUBMIT = Button(pnl, 2, "Submit")
        self.Bind(wx.EVT_BUTTON, self.OnSubmit, id=2)
        vbox.Add(SUBMIT, 0, wx.EXPAND | wx.ALL, 5)

        pnl.SetSizerAndFit(vbox)
        self.Fit()
        self.SetMinSize(self.GetEffectiveMinSize())

    def OnSubmit(self, *args):
        sel = self.OFFSETS.GetSelection()
        offset = self.MANUAL.GetValue()

        if offset != "":
            if len(offset) > 6:
                check = offset[-7:-6]
                if check == "1" or check == "9":
                    check = "1"
                else:
                    check = ""
                offset = check+offset[-6:].zfill(6)
            self.NewEggOffset = offset
            self.EndModal(wx.ID_OK)
        elif sel != -1:
            new_offset = self.OFFSETS.GetString(sel)[2:]
            self.NewEggOffset = new_offset
            self.EndModal(wx.ID_OK)

    def OnSearch(self, *args):
        self.OFFSETS.Clear()
        search = "\xff"*self.num
        with open(Globals.OpenRomName, "r+b") as rom:
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
                    self.OFFSETS.Append(hex(offset))
                    x = (1,True)
                    start = offset+len(search)

class NumberofEvosChanger(wx.Dialog):
    def __init__(self, frame, parent=None, *args, **kw):
        wx.Dialog.__init__(self, parent=parent, id=wx.ID_ANY)
        self.SetWindowStyle( self.GetWindowStyle() | wx.STAY_ON_TOP | wx.RESIZE_BORDER )


        self.InitUI()
        self.SetTitle("Change Number of Evolutions per 'MON")
        self.ShowModal()
        self.frame = frame

    def InitUI(self):
        pnl = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        txt = wx.StaticText(pnl, -1, "This is the first ever tool to change the number of\nevolutions a 'MON can have. Due to ASM limitations,\nthe number of new evolutions has to be a power of 2\nor just 5. Anything else requires custom ASM that\nwould require a repoint of a lot of things. So, let's get\nstarted!\n\n\nPlease pick a new number of evolutions:",style=wx.TE_CENTRE)
        vbox.Add(txt, 0, wx.EXPAND | wx.ALL, 5)

        self.choices = ["4","5","8","16","32"]

        self.NewNumberChoices = ComboBox(pnl, -1, choices=self.choices,
                                                    style=wx.SUNKEN_BORDER, size=(100, -1))
        vbox.Add(self.NewNumberChoices, 0, wx.EXPAND | wx.ALL, 5)

        txt2 = wx.StaticText(pnl, -1, "Now, you can either search for a free space offset or\n specify a manual offset for the new table.\nNOTE: Manual offsets are not checked\nfor free space content.",style=wx.TE_CENTRE)
        vbox.Add(txt2, 0, wx.EXPAND | wx.ALL, 5)

        self.OFFSETS = wx.ListBox(pnl, -1)
        vbox.Add(self.OFFSETS, 0, wx.EXPAND | wx.ALL, 5)

        SEARCH = Button(pnl, 1, "Search")
        self.Bind(wx.EVT_BUTTON, self.OnSearch, id=1)
        vbox.Add(SEARCH, 0, wx.EXPAND | wx.ALL, 5)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        manual_txt = wx.StaticText(pnl, -1, "Manual Offset: 0x",style=wx.TE_CENTRE)
        hbox.Add(manual_txt, 0, wx.ALL | wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
        self.MANUAL = wx.TextCtrl(pnl, -1,style=wx.TE_CENTRE, size=(100,-1))
        hbox.Add(self.MANUAL, 0, wx.ALL | wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
        vbox.Add(hbox, 0, wx.EXPAND | wx.ALL, 0)

        SUBMIT = Button(pnl, 2, "Submit")
        self.Bind(wx.EVT_BUTTON, self.OnSubmit, id=2)
        vbox.Add(SUBMIT, 0, wx.EXPAND | wx.ALL, 5)

        txt3 = wx.StaticText(pnl, -1, "\n\nA huge credit goes to DoesntKnowHowToPlay, who\ndiscovered how this can be done and kept notes\nabout it. Drop him a thank you if you really like it!",style=wx.TE_CENTRE)
        vbox.Add(txt3, 0, wx.EXPAND | wx.ALL, 5)

        pnl.SetSizerAndFit(vbox)
        self.Fit()
        self.SetMinSize(self.GetEffectiveMinSize())

    def OnSubmit(self, *args):
        sel = self.OFFSETS.GetSelection()
        _offset_ = self.MANUAL.GetValue()
        new_number = self.NewNumberChoices.GetSelection()
        new_number = int(self.choices[new_number])
        EvolutionsPerPoke = int(Globals.INI.get(Globals.OpenRomID, "EvolutionsPerPoke"), 0)
        if new_number == EvolutionsPerPoke:
            ComeOn = wx.MessageDialog(self,
                                "Look, you are supposed to change the number of evolutions. Haha, everyone makes mistakes. I would pick a different number.",
                                "What's the purpose?",
                                wx.OK)
            ComeOn.ShowModal()
            return
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

        ##copy table
        LengthOfOneEntry = int(Globals.INI.get(Globals.OpenRomID, "LengthOfOneEntry"), 0)
        EvolutionTable = int(Globals.INI.get(Globals.OpenRomID, "EvolutionTable"), 0)
        numberofpokes = int(Globals.INI.get(Globals.OpenRomID, "numberofpokes"), 0)

        readlength = EvolutionsPerPoke*LengthOfOneEntry*numberofpokes

        with open(Globals.OpenRomName, "r+b") as rom:
            rom.seek(EvolutionTable)
            entiretable = rom.read(readlength)

            table = []

            if new_number < EvolutionsPerPoke:
                while entiretable != "":
                    split = entiretable[:LengthOfOneEntry*EvolutionsPerPoke]
                    split = split[:new_number*LengthOfOneEntry]
                    table.append(split)
                    entiretable = entiretable[LengthOfOneEntry*EvolutionsPerPoke:]
            else:
                while entiretable != "":
                    split = entiretable[:LengthOfOneEntry*EvolutionsPerPoke]
                    split += "\x00"*(LengthOfOneEntry)*(new_number-EvolutionsPerPoke)
                    table.append(split)
                    entiretable = entiretable[LengthOfOneEntry*EvolutionsPerPoke:]
            int_offset = int(_offset_, 16)
            rom.seek(int_offset)
            for entry in table:
                rom.write(entry)
        ##write new pointers.
        EvolutionTablePointers = []
        list_pointers = Globals.INI.get(Globals.OpenRomID, "EvolutionTablePointers").split(",")

        for offset in list_pointers:
            EvolutionTablePointers.append(int(offset, 0))

        _offset_ = int(_offset_,16)+0x8000000
        _offset_ = hex(_offset_).lstrip("0x").rstrip("L").zfill(8)

        pointer = make_pointer(_offset_)
        pointer = get_hex_from_string(pointer)

        with open(Globals.OpenRomName, "r+b") as rom:
            for offset in EvolutionTablePointers:
                rom.seek(offset)
                rom.write(pointer)
        ##Ammend the ini

        _offset_ = int(_offset_,16)-0x8000000
        _offset_ = hex(_offset_).rstrip("L")

        Globals.INI.set(Globals.OpenRomID, "EvolutionTable", _offset_)
        Globals.INI.set(Globals.OpenRomID, "EvolutionsPerPoke", str(new_number))

        with open("PokeRoms.ini", "w") as PokeRomsIni:
            Globals.INI.write(PokeRomsIni)

        ##fill table with FF
        with open(Globals.OpenRomName, "r+b") as rom:
            rom.seek(EvolutionTable)
            for n in range(readlength):
                rom.write("\xFF")
        ##Adjust the rom for the new table
        change1 = [] #-> lsl r0, r6, #0x1 (70 00)
        tmp = Globals.INI.get(Globals.OpenRomID, "OffsetsToChangeTolslr0r60x1").split(",")
        for offset in tmp:
            change1.append(int(offset, 0))
        if new_number == 4: write = "3000"
        elif new_number == 8: write = "7000"
        elif new_number == 16: write = "B000"
        elif new_number == 32: write = "F000"
        else: write = "F019"

        change1write = unhexlify(write)

        with open(Globals.OpenRomName, "r+b") as rom:
            for offset in change1:
                rom.seek(offset, 0)
                rom.write(change1write)

        change2 = [] #04 -> 07
        tmp = Globals.INI.get(Globals.OpenRomID, "OffsetsToChangeToNewMinus1").split(",")
        for offset in tmp:
            change2.append(int(offset, 0))

        change2write = get_hex_from_string(str(hex(new_number-1)[2:]))

        with open(Globals.OpenRomName, "r+b") as rom:
            for offset in change2:
                rom.seek(offset, 0)
                rom.write(change2write)

        TheShedinjaFix = int(Globals.INI.get(Globals.OpenRomID, "LengthOfOneEntry"), 0)
        code = Globals.INI.get(Globals.OpenRomID, "gamecode")

        if code != "AXVE" and code != "AXPE":
            if new_number == 4: write = "0000"
            elif new_number == 8: write = "4000"
            elif new_number == 16: write = "8000"
            elif new_number == 32: write = "C000"
            else: write = "5044"
        else:
            if new_number == 4: write = "B90089460000"
            elif new_number == 8: write = "F90089460000"
            elif new_number == 16: write = "390189460000"
            elif new_number == 32: write = "790189460000"
            else: write = "B9008946C819"

        TheShedinjaFixWrite = unhexlify(write)

        with open(Globals.OpenRomName, "r+b") as rom:
            rom.seek(TheShedinjaFix, 0)
            rom.write(TheShedinjaFixWrite)

        change3 = []
        tmp = Globals.INI.get(Globals.OpenRomID, "ChangeToNewNumberTimes8").split(",")
        for offset in tmp:
            change3.append(int(offset, 0))

        change3write = get_hex_from_string(str(hex(new_number*8)[2:]))

        with open(Globals.OpenRomName, "r+b") as rom:
            for offset in change3:
                rom.seek(offset, 0)
                rom.write(change3write)

            ##Tell the user it worked, close, and reload data.
            #Small fix for some weird bytes that get written. Shhh, don't tell anyone.....
            rom.seek(8)
            rom.write("\x69\x9A")

        self.OnClose()
        DONE = wx.MessageDialog(None,
                                "Table has been moved, ini has been ammended,\nand evolutions have been changed.:)\n\n\nReloading 'MON Data.",
                                "Done!",
                                wx.OK)
        DONE.ShowModal()
        self.frame.tabbed_area.PokeDataTab.tabbed_area.reload_tab_data()

    def OnSearch(self, *args):
        #EvolutionsPerPoke = int(Globals.INI.get(Globals.OpenRomID, "EvolutionsPerPoke"), 0)
        LengthOfOneEntry = int(Globals.INI.get(Globals.OpenRomID, "LengthOfOneEntry"), 0)
        numberofpokes = int(Globals.INI.get(Globals.OpenRomID, "numberofpokes"), 0)

        NewEvolutionsPerPoke = self.NewNumberChoices.GetSelection()
        if NewEvolutionsPerPoke == -1:
            return
        NewEvolutionsPerPoke = int(self.choices[NewEvolutionsPerPoke])

        length = LengthOfOneEntry*NewEvolutionsPerPoke*numberofpokes

        self.OFFSETS.Clear()
        search = "\xff"*length
        with open(Globals.OpenRomName, "r+b") as rom:
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

    def OnClose(self, *args):
        self.Close()

class POKEDEXEntryRepointer(wx.Dialog):
    def __init__(self, parent=None, need=None, repoint_what=None, *args, **kw):
        wx.Dialog.__init__(self, parent=parent, id=wx.ID_ANY)
        self.SetWindowStyle( self.GetWindowStyle() | wx.STAY_ON_TOP | wx.RESIZE_BORDER )

        self.num = need
        self.repoint = repoint_what

        self.InitUI()
        self.OnSearch()
        self.SetTitle("Repoint 'Dex Entry")

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

        self.cb = wx.CheckBox(self, -1, 'Fill old entry with 0xFF?', (10, 10))
        self.cb.SetValue(True)
        vbox.Add(self.cb, 0, wx.ALL|wx.ALIGN_CENTER, 5)

        OK = self.CreateButtonSizer(wx.OK)
        vbox.Add(OK, 0, wx.EXPAND | wx.ALL, 5)

        txt3 = wx.StaticText(self, -1, "______________________________",style=wx.TE_CENTRE)
        vbox.Add(txt3, 0, wx.EXPAND | wx.ALL, 15)

        self.SetSizerAndFit(vbox)
        self.Fit()
        self.SetMinSize(self.GetEffectiveMinSize())

    def GetOffset(self, *args):
        global returned_offset
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

        try: int(_offset_, 16)
        except: return
        b = wx.StaticBox(pnl, label='Colors')
        sbs = wx.StaticBoxSizer(sb, orient=wx.VERTICAL)
        sbs.Add(wx.RadioButton(pnl, label='256 Colors',
            style=wx.RB_GROUP))
        sbs.Add(wx.RadioButton(pnl, label='16 Colors'))
        sbs.Add(wx.RadioButton(pnl, label='2 Colors'))
        returned_offset = _offset_

    def OnSearch(self, *args):
        self.OFFSETS.Clear()
        search = "\xff"*self.num
        with open(Globals.OpenRomName, "r+b") as rom:
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
