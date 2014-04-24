from lib.Tools.RecoveryINI import *
from GLOBALS import *

class Recovery:
    def __init__()):
        with open(GLOBALS.OpenRomName, "r+b") as rom:
            rom.seek(0xAC)
            self.gamecode = rom.read(4)
            if self.gamecode not in RecoveryIni.INI:
                self.NoRecovery = True
                return
            else:
                self.NoRecovery = False
                self.INI = RecoveryIni.INI[self.gamecode]
                self.Recover(rom)
            
    def Recover(rom):
        for name, offset in self.INI.iteritems():
            pass
        
class RecoveryPrompt(wx.Dialog):
    def __init__(self, *args, **kw):
        wx.Dialog.__init__(self, parent=None, id=wx.ID_ANY)
        self.SetWindowStyle( self.GetWindowStyle() | wx.RESIZE_BORDER )
        
        self.num = None
        
        self.InitUI()
        self.SetTitle("Repoint")
        
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
