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
        
        self.InitUI()
        self.SetTitle("Ini Recovery")
        
    def InitUI(self):
        pnl = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        txt = wx.StaticText(pnl, -1, "An ini that has been corrupted can often be recovered by reading the offsets of each table from the pointers to said tables. This function will attempt to do just that.")
        vbox.Add(txt, 0, wx.EXPAND | wx.ALL, 5)
        
        txt2 = wx.StaticText(pnl, -1, "\nBefore I recover the tables, I need some info on how big they were... All of these numbers can be changed later in the ini if need be.\n")
        vbox.Add(txt2, 0, wx.EXPAND | wx.ALL, 5)
        
        PokeHBox = wx.BoxSizer(wx.HORIZONTAL)
        vbox.Add(PokeHBox, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5)
        Poketxt = wx.StaticText(pnl, -1, "TOTAL Number of 'mons: ")
        vbox.Add(Poketxt, 0, wx.EXPAND | wx.ALL, 5)
        self.Pokemon = wx.SpinCtrl(pnl, -1,style=wx.TE_CENTRE, size=(100,-1))
        self.Pokemon.SetRange(0,1020)
        self.Pokemon.SetValue(412)
        PokeHBox.Add(self.Pokemon, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT, 5)
        
        MoveHBox = wx.BoxSizer(wx.HORIZONTAL)
        vbox.Add(MoveHBox, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5)
        Movetxt = wx.StaticText(pnl, -1, "Number of Moves: ")
        vbox.Add(Movetxt, 0, wx.EXPAND | wx.ALL, 5)
        self.Move = wx.SpinCtrl(pnl, -1,style=wx.TE_CENTRE, size=(100,-1))
        self.Move.SetRange(0,0xFFFF)
        self.Move.SetValue()
        MoveHBox.Add(self.Move, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT, 5)
        
        ItemHBox = wx.BoxSizer(wx.HORIZONTAL)
        vbox.Add(ItemHBox, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5)
        Itemtxt = wx.StaticText(pnl, -1, "Number of Items: ")
        vbox.Add(Itemtxt, 0, wx.EXPAND | wx.ALL, 5)
        self.Item = wx.SpinCtrl(pnl, -1,style=wx.TE_CENTRE, size=(100,-1))
        self.Item.SetRange(0,0xFFFF)
        self.Item.SetValue()
        ItemHBox.Add(self.Item, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT, 5)
        
        TypeHBox = wx.BoxSizer(wx.HORIZONTAL)
        vbox.Add(TypeHBox, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5)
        Typetxt = wx.StaticText(pnl, -1, "Number of Types: ")
        vbox.Add(Typetxt, 0, wx.EXPAND | wx.ALL, 5)
        self.Type = wx.SpinCtrl(pnl, -1,style=wx.TE_CENTRE, size=(100,-1))
        self.Type.SetRange(0,0xFFFF)
        self.Type.SetValue()
        TypeHBox.Add(self.Type, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT, 5)
        
        AbilityHBox = wx.BoxSizer(wx.HORIZONTAL)
        vbox.Add(AbilityHBox, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5)
        Abilitytxt = wx.StaticText(pnl, -1, "Number of Abilities: ")
        vbox.Add(Abilitytxt, 0, wx.EXPAND | wx.ALL, 5)
        self.Ability = wx.SpinCtrl(pnl, -1,style=wx.TE_CENTRE, size=(100,-1))
        self.Ability.SetRange(0,0xFFFF)
        self.Ability.SetValue()
        AbilityHBox.Add(self.Ability, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT, 5)
        
        SUBMIT = Button(pnl, 2, "Submit")
        self.Bind(wx.EVT_BUTTON, self.OnSubmit, id=2)
        vbox.Add(SUBMIT, 0, wx.EXPAND | wx.ALL, 5)
        
        pnl.SetSizerAndFit(vbox)
        self.Fit()
        self.SetMinSize(self.GetEffectiveMinSize())
