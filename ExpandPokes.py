# -*- coding: utf-8 -*- 

from __future__ import division
import wx, os, ConfigParser, sys
from binascii import hexlify, unhexlify
from Button import *

def RepointPokes():
    #Need:
    NewNumberOfPokes = None
    NewDexSize = None
    RAMOffset = None
    #-#-#-#
    with open(rom.name, "r+b") as rom:
        #Write JPAN's hack.
        with open("SBRTable.bin", "rb") as table:
            NewBlockTable = table.read()
            rom.seek(0x3FEC94)
            rom.write(NewBlockTable)
        with open("SaveBlockRecycle.bin", "rb") as SBR:
            JPANsSBR = SBR.read()
            rom.seek("""OFFSET""")
            rom.write(JPANsSBR)
        rom.seek(0xD991E)
        rom.write("\x38\x47")
        rom.seek(0xD995C)
        offset = hex("""OFFSET"""+0x8000061).rstrip("L").lstrip("0x").zfill(8)
        offset = make_pointer(offset)
        offset = unhexlify(offset)
        rom.write(offset)
        rom.seek(0xD9EDC)
        offset = hex("""OFFSET"""+0x8000001).rstrip("L").lstrip("0x").zfill(8)
        offset = make_pointer(offset)
        offset = unhexlify(offset)
        rom.write("\x00\x48\x00\x47"+offset)
        rom.seek(0x13b8c2)
        rom.write("\x1D\xE0")
        #Begin to follow Doesnt's tutorial
        ##Step 1: Write the seen/caught flags data.
        while NewDexSize % 8 != 0:
            NewDexSize += 1
        NeededFlagBytes = int(NewDexSize/8)
        #Seen Flags
        #----Writing Flag Changes
        SeenFlagsPoint = make_pointer(RAMOffset)
        SeenFlagsPoint = unhexlify(SeenFlagsPoint)
        rom.seek(0x104B10)
        rom.write(SeenFlagsPoint)
        rom.seek(0x104B00)
        rom.write("\x00"*4)
        #----Reading Flag Changes
        rom.seek(0x104B94)
        rom.write(SeenFlagsPoint)
        rom.seek(0x104B6A)
        rom.write("\x01\x1C\x00\x00")
        rom.seek(0x104B78)
        rom.write("\x1A\xE0")
        #Caught Flags
        #----Writing Flag Changes
        tmp = (RAMOffset, 16)+NeededFlagBytes
        tmp = hex(tmp).rstrip("L").lstrip("0x").zfill(8)
        CaughtFlagsPoint = make_pointer(tmp)
        CaughtFlagsPoint = unhexlify(CaughtFlagsPoint)
        rom.seek(0x104B5C)
        rom.write(CaughtFlagsPoint)
        rom.seek(0x104B16)
        rom.write("\x00"*6)
        rom.seek(0x104B26)
        rom.write("\x16\xE0")
        #----Reading Flag Changes
        rom.seek(0x104BB8)
        rom.write(CaughtFlagsPoint)
        rom.seek(0x104BA2)
        rom.write("\x01\x1C\x00\x00")
        #Skip extra tables
        rom.seek(0x104B34)
        rom.write("\x0F\xE0")
        ##Step 2: Repoint Goddamn everything
        TEMP = "\xCE\xBF\xC7\xCA\xFF\xFF\xFF\xFF\xFF\xFF\xFF"
        
        
class PokemonExpander(wx.Dialog):
    def __init__(self, rom, ini, parent=None, *args, **kw):
        wx.Dialog.__init__(self, parent=parent, id=wx.ID_ANY)
        self.SetWindowStyle( self.GetWindowStyle() | wx.STAY_ON_TOP | wx.RESIZE_BORDER )
        
        self.offset = None
        self.num = need
        self.repoint = repoint_what
        self.rom = rom
        self.InitUI()
        self.SetTitle("'MON Expander")
        
    def InitUI(self):
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        txt = wx.StaticText(self, -1, "Welcome to the first ever 'mon expander.\n This tool will take care of all of the heavy lifting.\n All the user has to do is supply a start offset\n to begin searching for free space. I did not\n set this program up to ask you for every single\n offset because I felt it would be awfully boring. So, all\n you have to do is chose one offset and then sit back\n and relax and I will dynamically search for free space\n after it and move any and all tables and expand them!:D\n\n",style=wx.TE_CENTRE)
        vbox.Add(txt, 0, wx.EXPAND | wx.ALL, 5)
        
        txt = wx.StaticText(self, -1, "How many TOTAL 'mons would you like?")
        vbox.Add(txt, 0, wx.EXPAND | wx.ALL, 5)
        
        self.NewPokeNum = wx.SpinCtrl(pnl, -1,style=wx.TE_CENTRE, size=(100,-1))
        self.NewPokeNum.SetRange(0,9999)
        vbox.Add(self.NewPokeNum, 0, wx.EXPAND | wx.ALL, 5)
        
        NumDexEntriesTxt = wx.StaticText(self, -1, "How many TOTAL 'dex entries would you like?")
        vbox.Add(NumDexEntriesTxt, 0, wx.EXPAND | wx.ALL, 5)
        
        self.NumDexEntriesTxt = wx.SpinCtrl(pnl, -1,style=wx.TE_CENTRE, size=(100,-1))
        self.NumDexEntriesTxt.SetRange(0,9999)
        vbox.Add(self.NumDexEntriesTxt, 0, wx.EXPAND | wx.ALL, 5)
        
        SEARCH = Button(pnl, 1, "Search")
        self.Bind(wx.EVT_BUTTON, self.OnSearch, id=1)
        vbox.Add(SEARCH, 0, wx.EXPAND | wx.ALL, 5)
        
        txt2 = wx.StaticText(self, -1, "Please choose an offset to repoint to or specify\na manual offset. If a manual offset is specified,\nthe list choice will be ignored.\n",style=wx.TE_CENTRE)
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
        
        RAM_Head = wx.StaticText(self, -1, "Please choose provide a RAM offset for\nthe seen/caught flags. If you don't know what\nthis is, don't change it.\n",style=wx.TE_CENTRE)
        vbox.Add(RAM_Head, 0, wx.EXPAND | wx.ALL, 5)
        
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        RAM_txt = wx.StaticText(self, -1, "RAM Offset: 0x",style=wx.TE_CENTRE)
        hbox2.Add(RAM_txt, 0, wx.EXPAND | wx.LEFT|wx.TOP|wx.BOTTOM, 5)
        self.RAM = wx.TextCtrl(self, -1,style=wx.TE_CENTRE, size=(100,-1))
        self.RAM.SetValue("0203c400")
        self.RAM.Bind(wx.EVT_TEXT, self.GetOffset)
        hbox2.Add(self.RAM, 0, wx.EXPAND | wx.RIGHT|wx.TOP|wx.BOTTOM, 5)
        vbox.Add(hbox2, 0, wx.EXPAND | wx.ALL, 0)
        
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
        self.RAM_offset = self.RAM.GetValue()
        if self.RAM_offset == "":
            self.RAM_offset = "0203c400"
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
        search = "\xff"*self.NewPokeNum.GetValue()*0x1C
        with open(self.rom, "r+b") as rom:
            rom.seek(0)
            read = rom.read()
            x = (0,True)
            start = 0x720000
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