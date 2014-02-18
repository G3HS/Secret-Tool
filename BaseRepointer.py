import wx

class Repointer(wx.Dialog):
    def __init__(self, rom, parent=None, need=None, repoint_what=None, *args, **kw):
        wx.Dialog.__init__(self, parent=parent, id=wx.ID_ANY)
        self.SetWindowStyle(self.GetWindowStyle()|wx.STAY_ON_TOP|wx.RESIZE_BORDER)
        
        self.offset = None
        self.num = need
        self.repoint = repoint_what
        self.rom = rom
        self.InitUI()
        self.OnSearch()
        self.SetTitle("Repoint "+self.repoint)
        
    def InitUI(self):
        vbox = wx.BoxSizer(wx.VERTICAL)
        
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